from modules.base import Base
from modules.utils import object_to_dict, strip_date
import tornado.gen
import re
import config
import base64
import os
from os.path import isfile, join
from werkzeug.security import generate_password_hash, check_password_hash



class Main(Base):

    @tornado.gen.coroutine
    def save_object(self, data):
        for k in self.__dict__:
            if k in data.keys():
                self.__setattr__(k, data[k])
        yield self.save()
        return self

    @tornado.gen.coroutine
    def edit_object(self, data):
        for k in self.__dict__:
            if k in data.keys():
                self.__setattr__(k, data[k])
        yield self.update()
        return self

class Users(Main):

    __tablename__ = 'users'

    def __init__(self, name=None, lastname=None, email=None, age=None,address=None,phone=None, status=None,
                 skype=None, about_me=None, linkedin=None, facebook=None, short_about=None, password_hash=None):
        self.name = name
        self.lastname = lastname
        self.email = email
        self.address = address
        self.age = age
        self.phone = phone
        self.status = status
        self.skype = skype
        self.about_me = about_me
        self.linkedin = linkedin
        self.facebook = facebook
        self.facebook = facebook
        self.facebook = facebook
        self.short_about = short_about
        self.password_hash = password_hash

    @tornado.gen.coroutine
    def change_pass(self, data):
        if not 'new_pass' in data:
            return {}
        if not 'check_pass' in data:
            return {'error': 'Confirm your password!'}
        if data['new_pass'] == data['check_pass']:
            yield self.db.execute(
                """ UPDATE users SET password_hash='{}'""".format(self.generate_password(data['new_pass'])) +
                " WHERE id='{}'".format(self.id))
            return {'success': 'You successful change password!'}
        else:
            return {'error': 'Fill in the same password!'}

    def generate_password(self, password):
        if password:
            return generate_password_hash(password,
                                          method='pbkdf2:sha256',
                                          salt_length=32)


    def verify_password(self, password):
        return self and check_password_hash(self.password_hash, password)

class Skills(Main):

    __tablename__ = 'skils'

    def __init__(self, name=None, user_id=None, kn_percent=None):
        self.name = name
        self.user_id = user_id
        self.kn_percent = kn_percent

class Educations(Main):

    __tablename__ = 'educations'

    def __init__(self, title=None, level=None, ed_from=None, ed_to=None, description=None):
        self.title = title
        self.level = level
        self.ed_from = ed_from
        self.ed_to = ed_to
        self.description = description

    @tornado.gen.coroutine
    def save_education(self, data):
        for k in self.__dict__:
            if k in data.keys():
                if k == 'ed_from' or k == 'ed_to':
                    if data[k]:
                        self.__setattr__(k, strip_date(data[k]))
                else:
                    self.__setattr__(k, data[k])

        yield self.save()
        return self

    @tornado.gen.coroutine
    def edit_education(self, data):
        for k in self.__dict__:
            if k in data.keys():
                if k == 'ed_from' or k == 'ed_to':
                    if data[k]:
                        self.__setattr__(k, strip_date(data[k]))
                else:
                    self.__setattr__(k, data[k])

        yield self.update()
        return self

class StaticData(Main):

    STATIC_TYPES = ['SKILL', 'EXPERIENCE', 'EDUCATION', 'PORTFOLIO', 'CONTACT', 'FOOTER', 'HEADER', 'TITLE']

    __tablename__ = 'static_data'

    def __init__(self, type=None, text=None):
        self.type = type
        self.text = text

    @tornado.gen.coroutine
    def edit_static(self, data):
        for k in self.__dict__:
            if k in data.keys():
                self.__setattr__(k, data[k])
        yield self.update(filter={'field': 'type', 'value': data['type']})
        return self

    @tornado.gen.coroutine
    def get_allowed_types(self):
        res = StaticData.STATIC_TYPES[:]
        data = yield self.fetch_all(StaticData)
        for element in data:
            if element.type in res:
                del res[res.index(element.type)]
        return res

class Projects(Main):

    __tablename__ = 'projects'

    def __init__(self, name=None, url=None, image_id=None):
        self.name = name
        self.url = url
        self.image_id = image_id

    @tornado.gen.coroutine
    def save_project(self, data):
        image = yield Images().save_image(data)
        self.name = data['name']
        self.url = data['url']
        self.image_id = image.id if image else config.DEFAULT_IMAGE_ID
        yield self.save()
        self.image_url = image.image_url()
        return self

    @tornado.gen.coroutine
    def edit_project(self, data):
        image = yield self.fetch(Images, data['image_id'])
        if 'file' in data:
            if image:
                yield image.delete_image()
            image = yield Images().save_image(data)
        self.name = data['name']
        self.url = data['url']
        if image:
            self.image_id = image.id
        self.update()
        self.image_url = image.image_url()
        return self

    @tornado.gen.coroutine
    def delete_project(self):
        image = yield self.fetch(Images, self.image_id)
        if image:
            yield image.delete_image()
        yield self.remove()

    @tornado.gen.coroutine
    def get_projects(self):
        projs = yield self.fetch_all(Projects, order_by={'field':'cr_tm','type':'DESC'})
        ret = []
        for project in projs:
            image = yield self.fetch(Images, project.image_id)
            project.get_image_url(image)
            ret.append(object_to_dict(project))
        return ret

    def get_image_url(self, image):
        if image:
            self.__setattr__('image_url', image.image_url())
        else:
            self.__setattr__('image_url', '/static/img/' + 'projects' + '/' + \
                            'default.png')

class Experience(Main):

    __tablename__ = 'experience'

    def __init__(self, user_id=None, title=None, subtitle=None, w_from=None, w_to=None, description=None):
        self.user_id = user_id
        self.title = title
        self.subtitle = subtitle
        self.w_from = w_from
        self.w_to = w_to
        self.description = description

    @tornado.gen.coroutine
    def save_experience(self, data):
        for k in self.__dict__:
            if k in data.keys():
                if k == 'w_from' or k == 'w_to':
                    if data[k]:
                        self.__setattr__(k, strip_date(data[k]))
                else:
                    self.__setattr__(k, data[k])

        yield self.save()
        return self

    @tornado.gen.coroutine
    def edit_experience(self, data):
        for k in self.__dict__:
            if k in data.keys():
                if k == 'w_from' or k == 'w_to':
                    if data[k]:
                        self.__setattr__(k, strip_date(data[k]))
                else:
                    self.__setattr__(k, data[k])

        yield self.update()
        return self

class Images(Main):

    __tablename__ = 'images'

    def __init__(self, folder_name=None, file_name=None, mime=None, size=None):
        self.folder_name = folder_name
        self.file_name = file_name
        self.mime = mime
        self.size = size

    @tornado.gen.coroutine
    def save_image(self, data):
        if 'file' in data:
            imgdataContent = data['file']['content']
            image_data = re.sub('^data:image/.+;base64,', '', imgdataContent)
            content = base64.b64decode(image_data)
            self.size = len(content)
            index = self.get_next_index_from_file(os.path.abspath("static") + '/img/projects/')
            self.file_name = 'file(' + str(index) + ')''.' + data['file']['mime'].split('/')[1]
            self.folder_name = 'projects'
            url = os.path.abspath("static") + '/img/projects/' + self.file_name
            with open(url, 'wb+') as f:
                f.write(content)
            try:
                yield self.save()
            except:
                os.remove(url)
            image = yield self.fetch_by(Images, file_name=self.file_name,folder_name=self.folder_name)
            return image
        image = yield self.fetch(Images, config.DEFAULT_IMAGE_ID)
        return image

    @tornado.gen.coroutine
    def delete_image(self):
        if self.id != config.DEFAULT_IMAGE_ID:
            os.remove(os.path.abspath("static") + '/img/projects/' + self.file_name)
            yield self.remove()

    def get_next_index_from_file(self, path):
        files = self.get_only_files_from_dir(path)
        index = 1
        for file in files:
            reg = re.match('([a-z_-]*[0-9_-]*)+(\((\d)+\))+\.\w+', file)
            if reg:
                if int(reg.group(3)) >= index:
                    index = int(reg.group(3)) + 1
        return index

    def get_only_files_from_dir(self, path):
        return [f for f in os.listdir(path) if isfile(join(path, f))]

    def image_url(self):
        return '/static/img/{0}/{1}'.format(self.folder_name, self.file_name)