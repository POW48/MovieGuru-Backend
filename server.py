import json

import tornado.ioloop
import tornado.web
import jieba

from model import Movie, Session, Staff


# jieba use lazy-load by default, force loading vocabulary
jieba.initialize()


rank_dict = json.load(open('../rank_dict.json'))


class JsonRequestHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        self.set_header('Content-Type', 'application/json')

    def write_json(self, stuff):
        self.write(json.dumps(stuff))


class SearchHandler(JsonRequestHandler):
    def get(self):
        global rank_dict

        query_text = self.get_query_argument('q')
        offset = self.get_query_argument('offset', default=0)
        limit = self.get_query_argument('limit', default=0)
        query_words = jieba.cut(query_text, cut_all=True)
        movie_set = dict()
        for word in query_words:
            if word in rank_dict:
                for movie_id, score in rank_dict[word][:10]:
                    if movie_id in movie_set:
                        movie_set[movie_id] += score[0]
                    else:
                        movie_set[movie_id] = score[0]

        search_result = []
        for movie_id in movie_set:
            search_result.append({ 'id': movie_id, 'score': movie_set[movie_id] })
        search_result.sort(key=lambda x: x['score'], reverse=True)

        if limit > 0:
            search_result = search_result[:limit]
        
        self.write_json(search_result)
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
