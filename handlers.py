import tornado.web
import tornado.gen
from modules.utils import format_date, send_message_async, dict_from_cursor_one, dict_from_cursor_all, \
    generate_password, verify_password, call_blocking_func
import datetime
from urllib import parse
import tornado.ioloop
import json
import re

class BaseHandler(tornado.web.RequestHandler):

    @property
    def db(self):
        return self.application.db

    @property
    def db_connect(self):
        return self.application.db_connect


    def get_current_user(self):
        return self.get_secure_cookie("email")

    @tornado.gen.coroutine
    def save_visitors(self, data):
        region = parse.unquote(data['region']).replace('"', '_').replace('*', '_').replace('/', '_').\
            replace('\\','_').replace("'", '_')
        yield self.db.execute("INSERT INTO visitors(ip, location, date, city, country, region, hostname)"
                              "VALUES('{0}','{1}','{2}','{3}','{4}','{5}','{6}')".
                              format(data['ip'], data['loc'], datetime.datetime.now(), data['city'], data['country'],
                                     region, data['hostname']))

    def write_error(self, status_code, **kwargs):
        if status_code in [403, 404, 500, 503]:
            self.render("admin/404.html")
        else:
            self.write('BOOM!')

    @tornado.gen.coroutine
    def get_current_user_dict(self):
        email = self.current_user.decode()
        cur = yield self.db.execute("SELECT * FROM users WHERE email='{}'".format(email))
        return dict_from_cursor_one(cur)

class HomeHandler(BaseHandler):

    @tornado.gen.coroutine
    def get(self):
        # response = requests.get('http://ipinfo.io')
        user = yield self.db.execute("SELECT * FROM users")
        skills = yield self.db.execute("SELECT * FROM skils ORDER BY kn_percent DESC")
        experiences = yield self.db.execute("SELECT * FROM experience")
        educations = yield self.db.execute("SELECT * FROM educations")
        projects = yield self.db.execute("SELECT * FROM projects")
        # tornado.ioloop.IOLoop.current().spawn_callback(self.save_visitors, response.json())
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


class AdminHandler(BaseHandler):

    @tornado.gen.coroutine
    def get(self):
        if not self.current_user:
            self.redirect('/admin/login')
        else:
            self.render("admin/index.html")

class FormsHandler(BaseHandler):

    @tornado.gen.coroutine
    def get(self):
        self.render("admin/form_component.html")

class EditPersonalInfo(BaseHandler):

    _actions = ['passchange', 'edit']
    __required_fields = []

    @tornado.web.authenticated
    @tornado.gen.coroutine
    def get(self):
        self.render("admin/personal_info.html")

    @tornado.web.authenticated
    @tornado.gen.coroutine
    def post(self):
        personal_info = yield self.db.execute("SELECT * FROM users")
        dict_info = dict_from_cursor_one(personal_info)
        self.write(dict_info)

    @tornado.web.authenticated
    @tornado.gen.coroutine
    def put(self, *args, **kwargs):
        data = json.loads(self.request.body.decode())
        action = re.match('(.*\?)([a-z]+)', self.request.uri).group(2)
        user = yield self.get_current_user_dict()
        if action in EditPersonalInfo._actions:
            if action == 'edit':
                yield self.db.execute(""" UPDATE users SET name='{name}',
                                                lastname='{lastname}',email='{email}',
                                                about_me='{about_me}', age={age},
                                                phone='{phone}',address='{address}',
                                                skype='{skype}',linkedin='{linkedin}',
                                                facebook='{facebook}' """.format(**data)+
                                                " WHERE id='{}'".format(user['id']))
                self.write({'data':data, 'success': 'You successful change your info!'})
            elif action == 'passchange' and data['new_pass']:
                if data['new_pass'] == data['check_pass']:
                    yield self.db.execute(""" UPDATE users SET password_hash='{}'""".format(generate_password(data['new_pass'])) +
                                          " WHERE id='{}'".format(user['id']))

                    self.write({'success': 'You successful change password!'})
                else:
                    self.write({'error': 'Fill in the same password!'})



class EditSkills(BaseHandler):

    _actions = ['change_password', 'edit']

    __required_fields = []

    @tornado.web.authenticated
    @tornado.gen.coroutine
    def get(self):
        self.render("admin/skills.html")

    @tornado.web.authenticated
    @tornado.gen.coroutine
    def post(self):
        skills = yield self.db.execute("SELECT * FROM skils WHERE user_id='{}'".format('984e586d-bd84-4ecc-b261-46b1c9c00c8c'))
        list_skills= dict_from_cursor_all(skills)
        self.write({'skills': list_skills})

    @tornado.web.authenticated
    @tornado.gen.coroutine
    def put(self, *args, **kwargs):
        data = json.loads(self.request.body.decode())
        user = yield self.get_current_user_dict()
        data['user_id'] = user['id']
        action = re.match('(.*\?)([a-z]+)', self.request.uri).group(2)
        if action in EditSkills._actions:
            if action == 'add':
                yield self.db.execute(""" INSERT INTO skils(name, kn_percent, user_id)
                                          VALUES('{0}', {1}, '{2}')""".format(data['name'],
                                                                              data['kn_percent'], data['user_id']))
            elif action == 'edit':
                yield self.db.execute(""" UPDATE skils SET name='{name}',
                                        kn_percent={kn_percent},user_id='{user_id}'""".format(**data) +
                                      """ WHERE id ='{}'""".format(data['id']))
            skills = yield self.db.execute(
                "SELECT * FROM skils WHERE user_id='{}'".format(user['id']))
            list_skills = dict_from_cursor_all(skills)
            self.write({'skills': list_skills})
        else:
            self.write({'skills': {}, 'error': 'Bad action!'})

    @tornado.web.authenticated
    @tornado.gen.coroutine
    def delete(self):
        user = yield self.get_current_user_dict()
        data = json.loads(self.request.body.decode())
        yield self.db.execute(
            "DELETE FROM skils WHERE id='{}'".format(data['id']))
        skills = yield self.db.execute(
            "SELECT * FROM skils WHERE user_id='{}'".format(user['id']))
        list_skills = dict_from_cursor_all(skills)
        self.write({'skills': list_skills})

class Login(BaseHandler):

    @tornado.gen.coroutine
    def get(self):
        if self.current_user:
            self.redirect('/admin')
        self.render("admin/login.html")

    @tornado.gen.coroutine
    def post(self):
        data = json.loads(self.request.body.decode())
        if not 'email' in data:
            self.write({'error': 'Please fill in email!'})
            return
        if not re.match('(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)', data['email']):
            self.write({'error': 'Incorrect email!'})
            return
        if not 'password' in data:
            self.write({'error': 'Please fill in password!'})
            return

        user = yield self.db.execute("SELECT * FROM users WHERE email='{}'".format(data['email']))
        cur = user.fetchone()
        if not cur:
            self.write({'error': 'User for this email does not exist!'})
            return
        if cur and verify_password(cur['password_hash'], data['password']):
            self.set_secure_cookie("email", data['email'])
            self.write({'login':'SUCCESS'})
        else:
            self.write({'error': 'Password for this email is wrong!'})

class Logout(BaseHandler):

    @tornado.web.authenticated
    @tornado.gen.coroutine
    def get(self):
        self.set_secure_cookie("email", '')
        self.redirect("/")

class ErrorHandler(tornado.web.ErrorHandler, BaseHandler):
    """
    Default handler gonna to be used in case of 404 error
    """
    pass








