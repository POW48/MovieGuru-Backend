import json

import tornado.ioloop
import tornado.web

from model import Movie, Session, Staff


class JsonRequestHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        self.set_header('Content-Type', 'application/json')

    def write_json(self, stuff):
        self.write(json.dumps(stuff))


class SearchHandler(JsonRequestHandler):
    def get(self):
        query = self.get_query_argument('q')
        offset = self.get_query_argument('offset', default=0)
        limit = self.get_query_argument('limit', default=0)
        self.write_json({
            'query': query,
            'offset': offset,
            'limit': limit
        })
        self.finish()


class QueryHandler(JsonRequestHandler):
    def get(self):
        session = Session()
        result = dict()
        for movie_id in self.get_query_argument('id').split(','):
            movie = session.query(Movie).filter(Movie.id == movie_id).one()
            data = dict()
            data['id'] = movie.id
            data['title'] = movie.title
            data['original_title'] = movie.original_title
            data['rating'] = str(movie.rating)
            data['introduction'] = movie.introduction
            data['poster'] = movie.poster
            data['year'] = movie.year
            data['languages'] = movie.languages
            data['countries'] = movie.countries
            data['publish_dates'] = movie.publish_dates
            data['review_count'] = movie.review_count
            data['durations'] = movie.durations
            data['is_tv'] = movie.is_tv
            # association with other entities
            data['genres'] = [genre.name for genre in movie.genres]
            data['tags'] = [tag.name for tag in movie.tags]
            data['aliases'] = [alias.alias for alias in movie.aliases]
            data['staffs'] = []
            for staff in movie.staffs:
                staff_json = dict()
                staff_record = session.query(Staff).filter(
                    Staff.id == staff.staff_id).one()
                staff_json['id'] = staff.staff_id
                staff_json['name'] = staff_record.name
                staff_json['abstract'] = staff_record.abstract
                staff_json['portrait'] = staff_record.portrait
                staff_json['roles'] = staff.get_roles_by_type()
                data['staffs'].append(staff_json)
            result[movie_id] = data
        self.write_json(result)
        self.finish()
        session.close()


def create_app():
    return tornado.web.Application([
        (r'/search', SearchHandler),
        (r'/movie', QueryHandler)
    ])


if __name__ == '__main__':
    app = create_app()
    app.listen(8080)
    tornado.ioloop.IOLoop.current().start()
