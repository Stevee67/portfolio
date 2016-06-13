import tornado.web
import tornado.gen
from modules.utils import format_date, send_message_async, dict_from_cursor_one, dict_from_cursor_all, \
    generate_password, verify_password, strip_date, get_next_index_from_file, merge_dict_by_kk

import datetime
from urllib import parse
import tornado.ioloop
import json
import re
import base64
import os
import config

STATIC_TYPES = ['SKILL', 'EXPERIENCE', 'EDUCATION', 'PORTFOLIO', 'CONTACT', 'FOOTER','HEADER', 'TITLE']


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


    @tornado.gen.coroutine
    def get_image(self, id):
        cur = yield self.db.execute("SELECT * FROM images WHERE id='{}'".format(id))
        return dict_from_cursor_one(cur)


    @tornado.gen.coroutine
    def upd_dict_with_img_url(self, data):
        new_list = []
        for element in data:
            new_dict = {}
            image = yield self.get_image(element['image_id'])
            if image:
                image_url = '/static/img/' + image['folder_name'] + '/' + \
                            image['file_name']
                new_dict['image_url'] = image_url
            else:
                new_dict['image_url'] = ''
            new_dict.update(element)
            new_list.append(new_dict)
        return new_list

class HomeHandler(BaseHandler):


    @tornado.gen.coroutine
    def get(self):
        # response = requests.get('http://ipinfo.io')
        try:
            user = yield self.db.execute("SELECT * FROM users WHERE email='{}'".format(config.SENDER_ADDRESS))
            skills = yield self.db.execute("SELECT * FROM skils ORDER BY kn_percent DESC")
            experiences = yield self.db.execute("SELECT * FROM experience")
            educations = yield self.db.execute("SELECT * FROM educations")
            projects = yield self.db.execute("SELECT * FROM projects")
            list_projects = yield self.upd_dict_with_img_url(dict_from_cursor_all(projects))
            static_data_cur = yield self.db.execute("SELECT * FROM static_data")
            # tornado.ioloop.IOLoop.current().spawn_callback(self.save_visitors, response.json())
            self.render("index.html", user=user.fetchone(),
                        skills=skills.fetchall(),
                        experiences=experiences.fetchall(),
                        educations=educations.fetchall(),
                        projects=list_projects,
                        static_data=merge_dict_by_kk(dict_from_cursor_all(static_data_cur), 'type', 'text'),
                        format_date=format_date)
        except Exception as error:
            self.write(str(error))
            try:
                self.db.connect()
            except Exception as error:
                self.write(str(error))
                self.finish()
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
        personal_info = yield self.db.execute("SELECT * FROM users WHERE email='{}'".format(config.SENDER_ADDRESS))
        dict_info = dict_from_cursor_one(personal_info)
        self.write(dict_info)
        self.finish()

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
        self.finish()



class EditSkills(BaseHandler):

    _actions = ['add', 'edit']

    __required_fields = []

    @tornado.web.authenticated
    @tornado.gen.coroutine
    def get(self):
        self.render("admin/skills.html")

    @tornado.web.authenticated
    @tornado.gen.coroutine
    def post(self):
        user = yield self.get_current_user_dict()
        skills = yield self.db.execute("SELECT * FROM skils WHERE user_id='{}'".format(user['id']))
        list_skills= dict_from_cursor_all(skills)
        self.write({'skills': list_skills})
        self.finish()

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
        self.finish()

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
        self.finish()

class EditExperience(BaseHandler):

    _actions = ['add', 'edit']

    __required_fields = []

    @tornado.web.authenticated
    @tornado.gen.coroutine
    def get(self):
        self.render("admin/experience.html")

    @tornado.web.authenticated
    @tornado.gen.coroutine
    def post(self):
        user = yield self.get_current_user_dict()
        experiences = yield self.db.execute("SELECT * FROM experience WHERE user_id='{}'".format(user['id']))
        list_experiences= dict_from_cursor_all(experiences)
        self.write({'experiences': list_experiences})
        self.finish()

    @tornado.web.authenticated
    @tornado.gen.coroutine
    def put(self, *args, **kwargs):
        data = json.loads(self.request.body.decode())
        user = yield self.get_current_user_dict()
        action = re.match('(.*\?)([a-z]+)', self.request.uri).group(2)
        data['w_from'] = strip_date(data['w_from'])
        data['w_to'] = strip_date(data['w_to'])
        if action in EditExperience._actions:
            if action == 'add':
                yield self.db.execute(""" INSERT INTO experience(title, subtitle, w_from, w_to, description, user_id)
                                          VALUES('{0}', '{1}', '{2}', '{3}', '{4}', '{5}')""".format(data['title'],
                                                                              data['subtitle'], data['w_from'],
                                                                              data['w_to'], data['description'], user['id']))
            elif action == 'edit':
                if data['w_to']:
                    yield self.db.execute(""" UPDATE experience SET
                                            title='{title}',
                                            subtitle='{subtitle}',
                                            w_from='{w_from}', w_to='{w_to}', description='{description}'"""
                                          .format(**data) + """ WHERE id ='{}'""".format(data['id']))
                else:
                    yield self.db.execute(""" UPDATE experience SET
                        title='{title}',
                        subtitle='{subtitle}',
                        w_from='{w_from}', w_to=NULL, description='{description}'"""
                                          .format(**data) + """ WHERE id ='{}'""".format(data['id']))
            experiences = yield self.db.execute("SELECT * FROM experience WHERE user_id='{}'".format(user['id']))
            list_experiences = dict_from_cursor_all(experiences)
            self.write({'experiences': list_experiences})
        else:
            self.write({'experiences': {}, 'error': 'Bad action!'})
        self.finish()

    @tornado.web.authenticated
    @tornado.gen.coroutine
    def delete(self):
        user = yield self.get_current_user_dict()
        data = json.loads(self.request.body.decode())
        yield self.db.execute(
            "DELETE FROM experience WHERE id='{}'".format(data['id']))
        experiences = yield self.db.execute(
            "SELECT * FROM experience WHERE user_id='{}'".format(user['id']))
        list_experiences = dict_from_cursor_all(experiences)
        self.write({'experiences': list_experiences})
        self.finish()

class EditEducation(BaseHandler):

    _actions = ['add', 'edit']

    __required_fields = []

    @tornado.web.authenticated
    @tornado.gen.coroutine
    def get(self):
        self.render("admin/education.html")

    @tornado.web.authenticated
    @tornado.gen.coroutine
    def post(self):
        educations = yield self.db.execute("SELECT * FROM educations")
        list_educations= dict_from_cursor_all(educations)
        self.write({'educations': list_educations})
        self.finish()

    @tornado.web.authenticated
    @tornado.gen.coroutine
    def put(self, *args, **kwargs):
        data = json.loads(self.request.body.decode())
        action = re.match('(.*\?)([a-z]+)', self.request.uri).group(2)
        data['ed_from'] = strip_date(data['ed_from'])
        data['ed_to'] = strip_date(data['ed_to'])
        if action in EditExperience._actions:
            if action == 'add':
                yield self.db.execute(""" INSERT INTO educations(title, level, ed_from, ed_to, description)
                                          VALUES('{0}', '{1}', '{2}', '{3}', '{4}')""".format(data['title'],
                                                                              data['level'], data['ed_from'],
                                                                              data['ed_to'], data['description']))
            elif action == 'edit':
                if data['ed_to']:
                    yield self.db.execute(""" UPDATE educations SET
                                            title='{title}',
                                            level='{level}',
                                            ed_from='{ed_from}', ed_to='{ed_to}', description='{description}'"""
                                          .format(**data) + """ WHERE id ='{}'""".format(data['id']))
                else:
                    yield self.db.execute(""" UPDATE educations SET
                        title='{title}',
                        level='{level}',
                        ed_from='{ed_from}', ed_to=NULL, description='{description}'"""
                                          .format(**data) + """ WHERE id ='{}'""".format(data['id']))
            educations = yield self.db.execute("SELECT * FROM educations")
            list_educations = dict_from_cursor_all(educations)
            self.write({'educations': list_educations})
        else:
            self.write({'educations': {}, 'error': 'Bad action!'})
        self.finish()

    @tornado.web.authenticated
    @tornado.gen.coroutine
    def delete(self):
        data = json.loads(self.request.body.decode())
        yield self.db.execute(
            "DELETE FROM educations WHERE id='{}'".format(data['id']))
        educations = yield self.db.execute(
            "SELECT * FROM educations")
        list_educations = dict_from_cursor_all(educations)
        self.write({'educations': list_educations})
        self.finish()

class EditStaticData(BaseHandler):

    _actions = ['add', 'edit']

    __required_fields = []

    @tornado.web.authenticated
    @tornado.gen.coroutine
    def get(self):
        self.render("admin/static.html")

    @tornado.web.authenticated
    @tornado.gen.coroutine
    def post(self):
        static_data = yield self.db.execute("SELECT * FROM static_data")
        list_static_data= dict_from_cursor_all(static_data)

        self.write({'static_data': list_static_data, 'types':self.get_allowed_types(list_static_data)})
        self.finish()

    @tornado.web.authenticated
    @tornado.gen.coroutine
    def put(self, *args, **kwargs):
        data = json.loads(self.request.body.decode())
        action = re.match('(.*\?)([a-z]+)', self.request.uri).group(2)
        if action in EditExperience._actions:
            if action == 'add':
                if not 'type' in data:
                    self.write({'static_data': {}, 'error': 'Static data is full or not selected!'})
                    return
                yield self.db.execute(""" INSERT INTO static_data(type, text)
                                          VALUES('{0}', '{1}')""".format(data['type'],
                                                                              data['text'] if 'text' in data else ''))
            elif action == 'edit':
                yield self.db.execute(""" UPDATE static_data SET
                                            type='{type}',
                                            text='{text}' """.format(**data) + """ WHERE type ='{}'""".format(data['type']))
            static_data = yield self.db.execute("SELECT * FROM static_data")
            list_static_data = dict_from_cursor_all(static_data)
            self.write({'static_data': list_static_data})
        else:
            self.write({'static_data': {}, 'error': 'Bad action!'})
        self.finish()

    @tornado.web.authenticated
    @tornado.gen.coroutine
    def delete(self):
        data = json.loads(self.request.body.decode())
        yield self.db.execute(
            "DELETE FROM static_data WHERE type='{}'".format(data['type']))
        static_data = yield self.db.execute(
            "SELECT * FROM static_data")
        list_static_data = dict_from_cursor_all(static_data)
        self.write({'static_data': list_static_data, 'types':self.get_allowed_types(list_static_data)})
        self.finish()

    def get_allowed_types(self, data):
        res = STATIC_TYPES[:]
        for element in data:
            if element['type'] in res:
                del res[res.index(element['type'])]
        return res

class Visitors(BaseHandler):

    _actions = ['add', 'edit']

    __required_fields = []

    @tornado.web.authenticated
    @tornado.gen.coroutine
    def get(self):
        self.render("admin/visitors.html")

    @tornado.web.authenticated
    @tornado.gen.coroutine
    def post(self):
        visitors = yield self.db.execute("SELECT * FROM visitors")
        list_visitors= dict_from_cursor_all(visitors)
        self.write({'visitors': list_visitors})
        self.finish()

    @tornado.web.authenticated
    @tornado.gen.coroutine
    def put(self, *args, **kwargs):
        data = json.loads(self.request.body.decode())
        action = re.match('(.*\?)([a-z]+)', self.request.uri).group(2)
        if action in EditExperience._actions:
            if action == 'add':
                if not 'type' in data:
                    self.write({'static_data': {}, 'error': 'Static data is full or not selected!'})
                    return
                yield self.db.execute(""" INSERT INTO static_data(type, text)
                                          VALUES('{0}', '{1}')""".format(data['type'],
                                                                              data['text'] if 'text' in data else ''))
            elif action == 'edit':
                yield self.db.execute(""" UPDATE static_data SET
                                            type='{type}',
                                            text='{text}' """.format(**data) + """ WHERE type ='{}'""".format(data['type']))
            static_data = yield self.db.execute("SELECT * FROM static_data")
            list_static_data = dict_from_cursor_all(static_data)
            self.write({'static_data': list_static_data})
        else:
            self.write({'static_data': {}, 'error': 'Bad action!'})
        self.finish()

    @tornado.web.authenticated
    @tornado.gen.coroutine
    def delete(self):
        data = json.loads(self.request.body.decode())
        yield self.db.execute(
            "DELETE FROM static_data WHERE type='{}'".format(data['type']))
        static_data = yield self.db.execute(
            "SELECT * FROM static_data")
        list_static_data = dict_from_cursor_all(static_data)
        self.write({'static_data': list_static_data, 'types':self.get_allowed_types(list_static_data)})
        self.finish()

    def get_allowed_types(self, data):
        res = STATIC_TYPES[:]
        for element in data:
            if element['type'] in res:
                del res[res.index(element['type'])]
        return res

class EditProjects(BaseHandler):

    _actions = ['add', 'edit']

    __required_fields = []

    @tornado.web.authenticated
    @tornado.gen.coroutine
    def get(self):
        self.render("admin/portfolio.html")

    @tornado.web.authenticated
    @tornado.gen.coroutine
    def post(self):
        projects = yield self.db.execute("SELECT * FROM projects")
        list_projects= dict_from_cursor_all(projects)
        self.write({'projects': list_projects})
        self.finish()

    @tornado.web.authenticated
    @tornado.gen.coroutine
    def put(self, *args, **kwargs):
        data = json.loads(self.request.body.decode())
        action = re.match('(.*\?)([a-z]+)', self.request.uri).group(2)
        if action in EditExperience._actions:
            if action == 'add':
                file = yield self.save_image(data)
                yield self.db.execute(""" INSERT INTO projects(name, url, image_id)
                                          VALUES('{0}', '{1}', '{2}')""".format(data['name'],
                                                                              data['url'], file['id'] if file else None))
            elif action == 'edit':
                cur = yield self.db.execute("SELECT id FROM images WHERE id='{}'".format(data['image_id']))
                image = dict_from_cursor_one(cur)
                if 'file' in data:
                    if image:
                        yield self.delete_image(image['id'])
                    image = yield self.save_image(data)
                if image:
                    yield self.db.execute(""" UPDATE projects SET name='{}',
                                              url='{}', image_id='{}'"""
                                              .format(data['name'], data['url'], image['id'])+
                                              """ WHERE id ='{}'""".format(data['id']))
                else:
                    yield self.db.execute(""" UPDATE projects SET name='{}',
                        url='{}'"""
                                          .format(data['name'], data['url']) +
                                          """ WHERE id ='{}'""".format(data['id']))



            projects = yield self.db.execute("SELECT * FROM projects")
            list_projects = dict_from_cursor_all(projects)
            self.write({'projects': list_projects})
        else:
            self.write({'projects': {}, 'error': 'Bad action!'})
        self.finish()

    @tornado.web.authenticated
    @tornado.gen.coroutine
    def delete(self):
        data = json.loads(self.request.body.decode())
        yield self.db.execute(
            "DELETE FROM projects WHERE id='{}'".format(data['id']))
        yield self.delete_image(data['image_id'])
        projects = yield self.db.execute(
            "SELECT * FROM projects")
        list_projects = dict_from_cursor_all(projects)
        self.write({'projects': list_projects})
        self.finish()

    @tornado.web.authenticated
    @tornado.gen.coroutine
    def delete_image(self, image_id):
        cur = yield self.db.execute("SELECT * FROM images WHERE id='{}'".format(image_id))
        image = dict_from_cursor_one(cur)
        os.remove(os.path.join(os.path.dirname(__file__), "static") + '/img/projects/' + image['file_name'])
        yield self.db.execute(
            "DELETE FROM images WHERE id='{}'".format(image['id']))


    @tornado.web.authenticated
    @tornado.gen.coroutine
    def save_image(self, data):
        if 'file' in data:
            imgdataContent = data['file']['content']
            image_data = re.sub('^data:image/.+;base64,', '', imgdataContent)
            content = base64.b64decode(image_data)
            size = len(content)
            index = get_next_index_from_file(os.path.join(os.path.dirname(__file__), "static") + '/img/projects/')
            file_name = 'file(' + str(index) + ')''.' + data['file']['mime'].split('/')[1]
            url = os.path.join(os.path.dirname(__file__), "static") + '/img/projects/' + file_name
            with open(url, 'wb+') as f:
                f.write(content)
            try:
                yield self.db.execute(""" INSERT INTO images(file_name, folder_name, mime, size)
                    VALUES('{0}', '{1}', '{2}', {3})""".format(file_name,
                                                          'projects', data['file']['mime'], size))
            except:
                os.remove(url)
            cur = yield self.db.execute(""" SELECT * FROM images WHERE file_name='{}'  AND folder_name='{}'""".format(file_name, 'projects'))
            return dict_from_cursor_one(cur)


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
        self.finish()

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








