from sqlalchemy import (Column, ForeignKey, Integer, Numeric, String, Table,
                        create_engine)
from sqlalchemy.ext.declarative import declarative_base
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

    genres = relationship('Genre', secondary=movie_genres,
                          back_populates='movies')
    tags = relationship('Tag', secondary=movie_tags, back_populates='movies')
    staffs = relationship('MovieStaff', back_populates='movie')
    aliases = relationship('Alias', back_populates='movie')

    def __repr__(self):
        return '<Movie(title="%s", original_title="%s")>' % (self.title, self.original_title)


engine = create_engine('sqlite:///:memory:', echo=True)
Session.configure(bind=engine)
Base.metadata.create_all(engine)

__all__ = ['Session', 'Movie', 'Staff', 'Alias', 'Tag', 'Genre', 'MovieStaff']
