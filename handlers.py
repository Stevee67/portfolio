import tornado.web
import tornado.gen
from modules.utils import format_date, send_message_async, send_message
import requests
import datetime
from urllib import parse
import tornado.ioloop

class BaseHandler(tornado.web.RequestHandler):

    @property
    def db(self):
        return self.application.db

    @property
    def db_connect(self):
        return self.application.db_connect

    def get_current_user(self):
        user_id = '984e586d-bd84-4ecc-b261-46b1c9c00c8c'
        if not user_id: return None
        return  self.db.execute("SELECT * FROM personal_info WHERE id = '{}'".format(user_id))

    @tornado.gen.coroutine
    def save_visitors(self, data):
        region = parse.unquote(data['region']).replace('"', '_').replace('*', '_').replace('/', '_').\
            replace('\\','_').replace("'", '_')
        yield self.db.execute("INSERT INTO visitors(ip, location, date, city, country, region, hostname)"
                              "VALUES('{0}','{1}','{2}','{3}','{4}','{5}','{6}')".
                              format(data['ip'], data['loc'], datetime.datetime.now(), data['city'], data['country'],
                                     region, data['hostname']))


class HomeHandler(BaseHandler):

    @tornado.gen.coroutine
    def get(self):
        response = requests.get('http://ipinfo.io')
        user = yield self.db.execute("SELECT * FROM personal_info")
        skills = yield self.db.execute("SELECT * FROM skils ORDER BY kn_percent DESC")
        experiences = yield self.db.execute("SELECT * FROM experience")
        educations = yield self.db.execute("SELECT * FROM educations")
        projects = yield self.db.execute("SELECT * FROM projects")
        tornado.ioloop.IOLoop.current().spawn_callback(self.save_visitors, response.json())
        self.render("index.html", user=user.fetchone(),
                                  skills=skills.fetchall(),
                                  experiences=experiences.fetchall(),
                                  educations=educations,
                                  projects=projects,
                                  format_date=format_date)

    @tornado.gen.coroutine
    def post(self):
        message = """ Message from %(from)s \n
            User email %(email)s \n
            Subject: %(subject)s \n
            Message: %(message)s""" % {'from': self.get_argument('name'),
                                       'email': self.get_argument('email'),
                                       'subject': self.get_argument('subject'),
                                       'message': self.get_argument('message')}

        tornado.ioloop.IOLoop.current().spawn_callback(send_message_async, message)


