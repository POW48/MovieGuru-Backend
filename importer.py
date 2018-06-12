import json
import os
import os.path

import jsonschema
from progressbar import ProgressBar

from model import Alias, Genre, Movie, MovieStaff, Session, Staff, Tag


class DoubanImporter:
    def __init__(self, schema_path='schema.json'):
        self.session = Session()
        self.genres_cache = dict()
        self.tags_cache = dict()
        self.staffs_cache = dict()
        schema = json.load(open(schema_path, 'r'))
        self.validator = jsonschema.Draft4Validator(schema)

    def get_or_create_genre(self, name):
        if name in self.genres_cache:
            return self.genres_cache[name]
        genre_entity = Genre(name=name)
        self.genres_cache[name] = genre_entity
        return genre_entity

    def get_or_create_tag(self, name):
        if name in self.tags_cache:
            return self.tags_cache[name]
        tag_entity = Tag(name=name)
        self.tags_cache[name] = tag_entity
        return tag_entity

    def get_or_create_staff(self, staff_json):
        staff_id = staff_json['id']
        if staff_id in self.staffs_cache:
            return self.staffs_cache[staff_id]
        staff_entity = Staff(id=staff_id,
                             name=staff_json['name'],
                             abstract=staff_json['abstract'],
                             portrait=staff_json['avatar']['large'])
        self.session.add(staff_entity)
        self.staffs_cache[staff_id] = staff_entity
        return staff_entity

    def _validate_json(self, movie_json):
        self.validator.validate(movie_json)

        # merge actors and directors
        staffs = movie_json['actors'] + movie_json['directors']

        # remove deplicated items in staff list
        deduplicator = set()
        new_staffs_list = []
        for staff_json in staffs:
            if staff_json['id'] in deduplicator:
                continue
            deduplicator.add(staff_json['id'])
            new_staffs_list.append(staff_json)
        movie_json['staffs'] = new_staffs_list

        # remove duplicated items in genre names
        new_genre_list = []
        for genre_name in movie_json['genres']:
            if genre_name not in new_genre_list:
                new_genre_list.append(genre_name)
        movie_json['genres'] = new_genre_list

        # remove duplicated items in aliases
        new_aka_list = []
        for aka in movie_json['aka']:
            if aka not in new_aka_list:
                new_aka_list.append(aka)
        movie_json['aka'] = new_aka_list

    def import_file(self, json_path):
        data = json.load(open(json_path, 'r'))

        try:
            self._validate_json(data)
        except:
            return

        for staff_json in data['staffs']:
            staff_entity = self.get_or_create_staff(staff_json)
            # Add record in movie_staffs
            self.session.add(MovieStaff(movie_id=data['id'],
                                        staff_id=staff_json['id'],
                                        type=MovieStaff.get_type_by_roles(staff_json['roles'])))

        mov = Movie(id=data['id'],
                    title=data['title'],
                    original_title=data['original_title'],
                    rating=float(data['rating']['value']),
                    introduction=data['intro'],
                    poster=data['pic']['large'],
                    year=(int(data['year']) if data['year'].isdigit() else None),
                    languages=','.join(data['languages']),
                    countries=','.join(data['countries']),
                    publish_dates=','.join(data['pubdate']),
                    review_count=int(data['review_count']),
                    durations=','.join(data['durations']),
                    is_tv=data['is_tv'],
                    # association with other entities
                    genres=[self.get_or_create_genre(genre)
                            for genre in data['genres']],
                    tags=[self.get_or_create_tag(tag['name'])
                          for tag in data['tags']],
                    aliases=[Alias(movie_id=data['id'], alias=alias)
                             for alias in data['aka']])

        self.session.add(mov)

    def import_folder(self, dataset_dir):
        file_list = [os.path.join(dataset_dir, name)
                     for name in os.listdir(dataset_dir)
                     if name.endswith('.json')]
        progress_bar = ProgressBar(max_value=len(file_list))
        for json_path in file_list:
            self.import_file(json_path)
            progress_bar.update(progress_bar.value + 1)
        progress_bar.finish()

    def commit(self):
        self.session.commit()


if __name__ == '__main__':
    importer = DoubanImporter()
    importer.import_folder('../Douban/data')
    importer.commit()
