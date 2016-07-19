import tornado.web
import tornado.gen
from modules.utils import format_date, send_message_async, merge_object_by_kk, paginaion, object_to_dict, success
import tornado.ioloop
import json
import re
import config
from modules.base import Base
from modules.models import Users, StaticData, Projects, Educations, Skills, Experience, Visitors


class HomeHandler(Base):

    @tornado.gen.coroutine
    def get(self):
        x_real_ip = self.request.headers.get("X-Real-IP")
        ip = x_real_ip or self.request.remote_ip
        user = yield self.fetch(Users, '984e586d-bd84-4ecc-b261-46b1c9c00c8c')
        static_data = yield self.fetch_all(StaticData)
        projects = yield Projects().get_projects()
        educations = yield self.fetch_all(Educations, order_by={'ed_from':'ASC'})
        skills = yield self.fetch_all(Skills, order_by={'kn_percent':'DESC'})
        experiences = yield self.fetch_all(Experience)
        yield Visitors().save_visitors(ip)
        self.render("index.html", user=user,
                    skills=skills,
                    experiences=experiences,
                    educations=educations,
                    projects=projects,
                    static_data=merge_object_by_kk(static_data, 'type', 'text'),
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


class AdminHandler(Base):

    @tornado.gen.coroutine
    def get(self):
        if not self.current_user:
            self.redirect('/admin/login')
        else:
            self.render("admin/index.html")

class EditPersonalInfo(Base):

    _actions = ['passchange', 'edit']

    @tornado.web.authenticated
    @tornado.gen.coroutine
    def get(self):
        self.render("admin/personal_info.html")

    @success
    @tornado.web.authenticated
    @tornado.gen.coroutine
    def post(self):
        personal_info = yield self.fetch_by(Users, email=config.SENDER_ADDRESS)
        return personal_info


    @tornado.web.authenticated
    @tornado.gen.coroutine
    def put(self, *args, **kwargs):
        data = json.loads(self.request.body.decode())
        action = re.match('(.*\?)([a-z]+)', self.request.uri).group(2)
        email = self.get_current_user()
        user = yield self.fetch_by(Users, email=email.decode())
        if action in EditPersonalInfo._actions:
            if action == 'edit':
                new_user = yield user.edit_object(data)
                self.write({'data':object_to_dict(new_user), 'success': 'You successful change your info!'})
            elif action == 'passchange':
                result = yield user.change_pass(data)
                self.write(result)
        self.finish()



class EditSkills(Base):

    _actions = ['add', 'edit']

    @tornado.web.authenticated
    @tornado.gen.coroutine
    def get(self):
        self.render("admin/skills.html")

    @success
    @tornado.web.authenticated
    @tornado.gen.coroutine
    def post(self):
        user = yield self.fetch_by(Users, email=self.current_user.decode())
        skills = yield self.fetch_all(Skills, filter_by={'user_id':user.id}, order_by={'kn_percent':'DESC'})
        return skills

    @success
    @tornado.web.authenticated
    @tornado.gen.coroutine
    def put(self, *args, **kwargs):
        data = json.loads(self.request.body.decode())
        user = yield self.fetch_by(Users, email=self.current_user.decode())
        data['user_id'] = user.id
        action = re.match('(.*\?)([a-z]+)', self.request.uri).group(2)
        if action in EditSkills._actions:
            if action == 'add':
                skill = yield Skills().save_object(data)
            else:
                old_sk = yield self.fetch(Skills, data['id'])
                skill = yield old_sk.edit_object(data)
            return skill
        else:
            raise Exception('Bad action')


    @tornado.web.authenticated
    @tornado.gen.coroutine
    def delete(self):
        data = json.loads(self.request.body.decode())
        skill = yield self.fetch(Skills, data['id'])
        skill.remove()
        self.finish()

class EditExperience(Base):

    _actions = ['add', 'edit']

    @tornado.web.authenticated
    @tornado.gen.coroutine
    def get(self):
        self.render("admin/experience.html")

    @success
    @tornado.web.authenticated
    @tornado.gen.coroutine
    def post(self):
        user = yield self.fetch_by(Users, email=self.current_user.decode())
        experiences = yield self.fetch_all(Experience, filter_by={'user_id':user.id},
                                           order_by={'w_from':'ASC'})
        return experiences

    @success
    @tornado.web.authenticated
    @tornado.gen.coroutine
    def put(self, *args, **kwargs):
        data = json.loads(self.request.body.decode())
        user = yield self.fetch_by(Users, email=self.current_user.decode())
        action = re.match('(.*\?)([a-z]+)', self.request.uri).group(2)
        data['user_id'] = user.id
        if action in EditExperience._actions:
            if action == 'add':
                experience = yield Experience().save_experience(data)
            else:
                old_experience = yield self.fetch(Experience, data['id'])
                experience = yield old_experience.edit_experience(data)
            return experience
        else:
            raise Exception('Bad action')

    @tornado.web.authenticated
    @tornado.gen.coroutine
    def delete(self):
        data = json.loads(self.request.body.decode())
        experience = yield self.fetch(Experience, data['id'])
        yield experience.remove()
        self.finish()

class EditEducation(Base):

    _actions = ['add', 'edit']

    @tornado.web.authenticated
    @tornado.gen.coroutine
    def get(self):
        self.render("admin/education.html")

    @success
    @tornado.web.authenticated
    @tornado.gen.coroutine
    def post(self):
        educations = yield self.fetch_all(Educations)
        return educations

    @success
    @tornado.web.authenticated
    @tornado.gen.coroutine
    def put(self, *args, **kwargs):
        data = json.loads(self.request.body.decode())
        action = re.match('(.*\?)([a-z]+)', self.request.uri).group(2)
        if action in EditExperience._actions:
            if action == 'add':
                education = yield Educations().save_education(data)
            else:
                old_education = yield self.fetch(Educations, data['id'])
                education = yield old_education.edit_education(data)
            return education
        else:
            raise Exception('Bad action')

    @tornado.web.authenticated
    @tornado.gen.coroutine
    def delete(self):
        data = json.loads(self.request.body.decode())
        education = yield self.fetch(Educations, data['id'])
        yield education.remove()
        self.finish()

class EditStaticData(Base):

    _actions = ['add', 'edit']

    @tornado.web.authenticated
    @tornado.gen.coroutine
    def get(self):
        self.render("admin/static.html")

    @success
    @tornado.web.authenticated
    @tornado.gen.coroutine
    def post(self):
        static_data = yield self.fetch_all(StaticData)
        types = yield StaticData().get_allowed_types()
        return {'data': [object_to_dict(data) for data in static_data], 'types': types}

    @success
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
                std = yield StaticData().save_object(data)
            else:
                old_std = yield self.fetch_by(StaticData, type=data['type'])
                std = yield old_std.edit_static(data)
            return std
        else:
            raise Exception('Bad action')

    @success
    @tornado.web.authenticated
    @tornado.gen.coroutine
    def delete(self):
        data = json.loads(self.request.body.decode())
        std = yield self.fetch(StaticData, data['id'])
        yield std.remove()
        types = yield StaticData().get_allowed_types()
        return types

class ListVisitors(Base):

    item_per_page = 25

    _actions = ['add', 'edit']

    @tornado.web.authenticated
    @tornado.gen.coroutine
    def get(self):
        self.render("admin/visitors.html", format_date=format_date)

    @success
    @tornado.web.authenticated
    @tornado.gen.coroutine
    def post(self):
        data = json.loads(self.request.body.decode())
        pages, list_visitors, count = yield paginaion(self.db, 'visitors', ListVisitors.item_per_page, data['page'])
        item_on_pages = str(data['page']*ListVisitors.item_per_page) if data['page'] != pages else str(count)
        return {'visitors': list_visitors,
                    'pages': pages,
                    'page': data['page'],
                    'count':  item_on_pages+'/'+str(count)}


class EditProjects(Base):

    _actions = ['add', 'edit']

    @tornado.web.authenticated
    @tornado.gen.coroutine
    def get(self):
        self.render("admin/portfolio.html")

    @success
    @tornado.web.authenticated
    @tornado.gen.coroutine
    def post(self):
        projects = yield Projects().get_projects()
        return projects

    @success
    @tornado.web.authenticated
    @tornado.gen.coroutine
    def put(self, *args, **kwargs):

        data = json.loads(self.request.body.decode())
        action = re.match('(.*\?)([a-z]+)', self.request.uri).group(2)
        if action in EditExperience._actions:
            if action == 'add':
                project = yield Projects().save_project(data)
            else:
                project = yield self.fetch(Projects, data['id'])
                yield project.edit_project(data)
            return project
        else:
            raise Exception('Bad action')

    @tornado.web.authenticated
    @tornado.gen.coroutine
    def delete(self):
        data = json.loads(self.request.body.decode())
        project = yield self.fetch(Projects, data['id'])
        yield project.delete_project()
        self.finish()



class Login(Base):

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

        user = yield self.fetch_by(Users, email=data['email'])
        if not user:
            self.write({'error': 'User for this email does not exist!'})
            return
        if user and user.verify_password(data['password']):
            self.set_secure_cookie("email", data['email'])
            self.write({'login':'SUCCESS'})
        else:
            self.write({'error': 'Password for this email is wrong!'})
        self.finish()


class Logout(Base):

    @tornado.web.authenticated
    @tornado.gen.coroutine
    def get(self):
        self.set_secure_cookie("email", '')
        self.redirect("/")

class ErrorHandler(tornado.web.ErrorHandler, Base):
    """
    Default handler gonna to be used in case of 404 error
    """
    pass


# 127.0.0.1 localhost.localdomain localhost localhost4.localdomain4 localhost4
# ::1 localhost6.localdomain6 localhost6 localhost.localdomain localhost
# 172.16.10.38 ex-std-node845.prod.rhcloud.com ex-std-node845









