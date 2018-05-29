from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Table, Column, Integer, String, Numeric, ForeignKey
from sqlalchemy.orm import relationship, sessionmaker

"""
Now that we have a “base”, we can define any number of mapped classes in terms of it.
"""
Base = declarative_base()
Session = sessionmaker()

TABLE_ID_LENGTH = 12


"""
Association table for movies and genres
"""
movie_genres = Table(
    'movie_genres',
    Base.metadata,
    Column('movie_id', ForeignKey('movies.id'), primary_key=True),
    Column('genre_name', ForeignKey('genres.name'), primary_key=True)
)


GENRE_NAME_LENGTH = 20


class Genre(Base):
    __tablename__ = 'genres'

    name = Column(String(GENRE_NAME_LENGTH), primary_key=True)
    movies = relationship('Movie',
                          secondary=movie_genres,
                          back_populates='genres')


"""
Association table for movies and tags
"""
movie_tags = Table(
    'movie_tags',
    Base.metadata,
    Column('movie_id', ForeignKey('movies.id'), primary_key=True),
    Column('tag_id', ForeignKey('tags.name'), primary_key=True)
)


TAG_NAME_LENGTH = 50


class Tag(Base):
    __tablename__ = 'tags'

    name = Column(String(TAG_NAME_LENGTH), primary_key=True)
    movies = relationship(
        'Movie',
        secondary=movie_tags,
        back_populates='tags'
    )


STAFF_NAME_LENGTH = 100


"""
Association table for movies and tags
"""
class MovieStaff(Base):
    __tablename__ = 'movie_staffs'
    movie_id = Column(ForeignKey('movies.id'), primary_key=True)
    staff_id = Column(ForeignKey('staffs.id'), primary_key=True)
    type = Column(Integer)
    movie = relationship('Movie', back_populates='staffs')
    staff = relationship('Staff', back_populates='movies')


class Staff(Base):
    __tablename__ = 'staffs'

    id = Column(String, primary_key=True)
    name = Column(String)
    movies = relationship('MovieStaff', back_populates='staff')

    def __repr__(self):
        return '<Staff(name="%s")>' % (self.name)


MOVIE_TITLE_LENGTH = 200


class Alias(Base):
    __tablename__ = 'aliases'

    id = Column(Integer, primary_key=True)
    movie_id = Column(String(TABLE_ID_LENGTH), ForeignKey('movies.id'))
    alias = Column(String(MOVIE_TITLE_LENGTH), nullable=False)

    movie = relationship('Movie', back_populates='aliases')


class Movie(Base):
    __tablename__ = 'movies'

    id = Column(String(TABLE_ID_LENGTH), primary_key=True)
    title = Column(String(MOVIE_TITLE_LENGTH), nullable=False)
    original_title = Column(String(MOVIE_TITLE_LENGTH), nullable=False)
    rating = Column(Numeric(1, 1))

    genres = relationship('Genre', secondary=movie_genres, back_populates='movies')
    tags = relationship('Tag', secondary=movie_tags, back_populates='movies')
    staffs = relationship('MovieStaff', back_populates='movie')
    aliases = relationship('Alias', back_populates='movie')


    def __repr__(self):
        return '<Movie(title="%s", original_title="%s")>' % (self.title, self.original_title)


def import_douban_dataset(schema_path, dataset_path):
    import json
    import jsonschema
    import os
    import os.path
    schema = json.load(open(schema_path, 'r'))
    validator = jsonschema.Draft4Validator(schema)
    session = Session()

    genres_cache = dict()
    tags_cache = dict()
    staffs_cache = dict()

    def get_genre(name):
        if name not in genres_cache:
            genre = Genre(name=name, movies=[])
            genres_cache[name] = genre
            return genre
        return genres_cache[name]

    def get_tag(name):
        if name not in tags_cache:
            tag = Tag(name=name, movies=[])
            tags_cache[name] = tag
            return tag
        return tags_cache[name]

    def get_staff(staff):
        staff_id = staff['id']
        if staff_id not in staffs_cache:
            staff = Staff(id=staff_id, name=staff['name'])
            staffs_cache[staff_id] = staff
            return staff
        return staffs_cache[staff_id]

    for json_path in [os.path.join(dataset_path, name) for name in os.listdir(dataset_path) if name.endswith('.json')]:
        data = json.load(open(json_path, 'r'))
        try:
            validator.validate(data)
        except jsonschema.ValidationError as error:
            print(error)
            continue

        staffs_id = set()
        for staff_json in data['actors']:
            # Detect duplicated items in actor list.
            # This is necessary because JSON schema cannot
            # ensure the uniqueness of elements in an array.
            if staff_json['id'] in staffs_id:
                continue
            staffs_id.add(staff_json['id'])
            staff_entity = get_staff(staff_json)
            # Add record in movie_staffs
            session.add(MovieStaff(movie_id=data['id'], staff_id=staff_json['id'], type=0)) # TODO: specify role here

        mov = Movie(
            id=data['id'],
            title=data['title'],
            rating=float(data['rating']['value']),
            original_title='',
            genres=[get_genre(genre_name) for genre_name in data['genres']],
            tags=[get_tag(tag['name']) for tag in data['tags']],
            aliases=[Alias(movie_id=data['id'], alias=alias) for alias in data['aka']])
        session.add(mov)

    # add staffs to session
    for staff_id, staff_entity in staffs_cache.items():
        session.add(staff_entity)

    session.commit()


if __name__ == '__main__':
    engine = create_engine('sqlite:///:memory:', echo=True)
    Session.configure(bind=engine)
    Base.metadata.create_all(engine)
    import_douban_dataset('schema.json', '../Douban/data')
