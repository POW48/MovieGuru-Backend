import json

from sqlalchemy import (Column, Boolean, ForeignKey, Integer, Float, String, Table,
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
all_role_names = [
    "编剧", "导演", "演员", "配音", "制片", "剪辑", "副导演",
    "摄影", "作曲", "服装设计", "艺术指导", "选角导演", "美术设计",
    "视觉特效", "动作指导", "布景师", "化妆师"
]
role_type_map = dict(zip(all_role_names, range(len(all_role_names))))

"""
Association table for movies and staffs
"""


class MovieStaff(Base):
    __tablename__ = 'movie_staffs'
    movie_id = Column(ForeignKey('movies.id'), primary_key=True)
    staff_id = Column(ForeignKey('staffs.id'), primary_key=True)
    type = Column(Integer)
    movie = relationship('Movie', back_populates='staffs')
    staff = relationship('Staff', back_populates='movies')

    @staticmethod
    def get_type_by_roles(roles):
        bit_pattern = 0
        for role in roles:
            bit_pattern = bit_pattern | (1 << role_type_map.get(role))
        return bit_pattern

    def get_roles_by_type(self):
        bit_pattern = int(self.type)
        roles = []
        for index, role in enumerate(all_role_names):
            if (bit_pattern & (1 << index)) > 0:
                roles.append(role)
        return roles


STAFF_ABSTRACT_LENGTH = 400
STAFF_PORTRAIT_URL_LENGTH = 512


class Staff(Base):
    __tablename__ = 'staffs'

    id = Column(String, primary_key=True)
    name = Column(String(STAFF_NAME_LENGTH))
    abstract = Column(String(STAFF_ABSTRACT_LENGTH))
    portrait = Column(String(STAFF_PORTRAIT_URL_LENGTH))
    movies = relationship('MovieStaff', back_populates='staff')

    def __repr__(self):
        return '<Staff(name="%s")>' % (self.name)


MOVIE_TITLE_LENGTH = 200
INTRODUCTION_LENGTH = 1000


class Alias(Base):
    __tablename__ = 'aliases'

    movie_id = Column(String(TABLE_ID_LENGTH),
                      ForeignKey('movies.id'), primary_key=True)
    alias = Column(String(MOVIE_TITLE_LENGTH), primary_key=True)

    movie = relationship('Movie', back_populates='aliases')


MOVIE_POSTER_URL_LENGTH = 512
MOVIE_LANGUAGES_LENGTH = 100
MOVIE_COUNTRIES_LENGTH = 100
MOVIE_PUBLISH_DATES_LENGTH = 100
MOVIE_DURATIONS_LENGTH = 100


class Movie(Base):
    __tablename__ = 'movies'

    # fields
    id = Column(String(TABLE_ID_LENGTH), primary_key=True)
    title = Column(String(MOVIE_TITLE_LENGTH), nullable=False)
    original_title = Column(String(MOVIE_TITLE_LENGTH), nullable=False)
    rating = Column(Float)
    introduction = Column(String(INTRODUCTION_LENGTH))
    poster = Column(String(MOVIE_POSTER_URL_LENGTH))
    year = Column(Integer, nullable=True)
    languages = Column(String(MOVIE_LANGUAGES_LENGTH))
    countries = Column(String(MOVIE_COUNTRIES_LENGTH))
    publish_dates = Column(String(MOVIE_PUBLISH_DATES_LENGTH))
    review_count = Column(Integer)
    durations = Column(String(MOVIE_DURATIONS_LENGTH))
    is_tv = Column(Boolean)

    # association with other entities
    genres = relationship('Genre', secondary=movie_genres,
                          back_populates='movies')
    tags = relationship('Tag', secondary=movie_tags, back_populates='movies')
    staffs = relationship('MovieStaff', back_populates='movie')
    aliases = relationship('Alias', back_populates='movie')

    def __repr__(self):
        return '<Movie(title="%s", original_title="%s")>' % (self.title, self.original_title)


SEARCH_WORD_LENGTH = 20


class SearchIndex(Base):
    __tablename__ = 'search_indices'

    movie_id = Column(ForeignKey('movies.id'), primary_key=True)
    words = Column(String(SEARCH_WORD_LENGTH))


engine = create_engine('sqlite:///../MovieGuru.sqlite')
Session.configure(bind=engine)
Base.metadata.create_all(engine)

__all__ = ['Session', 'Movie', 'Staff', 'Alias', 'Tag', 'Genre', 'MovieStaff']
