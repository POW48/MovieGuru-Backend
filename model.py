from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Table, Column, Integer, String, Numeric, ForeignKey
from sqlalchemy.orm import relationship

"""
Now that we have a “base”, we can define any number of mapped classes in terms of it.
"""
Base = declarative_base()


TABLE_ID_LENGTH = 12


"""
Association table for movies and genres
"""
movie_genres = Table(
    'movie_genres',
    Base.metadata,
    Column('movie_id', ForeignKey('movies.id'), primary_key=True),
    Column('genre_id', ForeignKey('genres.id'), primary_key=True)
)


class Genre(Base):
    __tablename__ = 'genres'

    id = Column(Integer, primary_key=True)
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
movie_staffs = Table(
    'movie_staffs',
    Base.metadata,
    Column('movie_id', ForeignKey('movies.id'), primary_key=True),
    Column('staff_id', ForeignKey('staffs.id'), primary_key=True),
    Column('type', Integer)
)


class Staff(Base):
    __tablename__ = 'staffs'

    id = Column(String, primary_key=True)
    name = Column(String)
    movies = relationship('Movie', secondary=movie_staffs, back_populates='staffs')

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
    tags = relationship('Tag', secondary=movie_tags, back_populates='tags')
    staffs = relationship('Staff', secondary=movie_staffs, back_populates='staffs')
    aliases = relationship('Alias', back_populates='movie')

    
    def __repr__(self):
        return '<Movie(title="%s", original_title="%s")>' % (self.title, self.original_title)


def import_douban_dataset(director):
    import json
    import jsonschema


if __name__ == '__main__':
    engine = create_engine('sqlite:///:memory:', echo=True)
    Base.metadata.create_all(engine)