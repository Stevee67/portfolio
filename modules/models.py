from modules.base import Base
from modules.utils import strip_date
import tornado.gen
import re
import config
import base64
import datetime
from urllib import parse
import os
from os.path import isfile, join
from werkzeug.security import generate_password_hash, check_password_hash
import geoip2.database



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

    def check_required_fields(self):
        if not hasattr(self, '_required_fields'):
            raise Exception('{0} object has not attribute _required_fields'.format(self.__class__.__name__))
        for k in self._required_fields:
            if k not in self.__dict__:
                return False
            if not self.__getattribute__(k):
                return False
        return True

    def check_date_frto(self, fr, to):
        if not fr:
            return False
        if not to:
            return True
        if fr>=to:
            return False
        return True


class Users(Main):

    __tablename__ = 'users'
    _required_fields = ['name', 'lastname', 'email', 'age']

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
    _required_fields = ['name', 'kn_percent']

    def __init__(self, name=None, user_id=None, kn_percent=None):
        self.name = name
        self.user_id = user_id
        self.kn_percent = kn_percent

class Educations(Main):

    __tablename__ = 'educations'
    _required_fields = ['title', 'level', 'ed_from']

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
    _required_fields = ['type']

    def __init__(self, type=None, text=None):
        self.type = type
        self.text = text

    @tornado.gen.coroutine
    def edit_static(self, data):
        for k in self.__dict__:
            if k in data.keys():
                self.__setattr__(k, data[k])
        yield self.update(filter={'type',data['type']})
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
    _required_fields = ['name', 'url', 'image_id']

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
        projs = yield self.fetch_all(Projects, order_by={'cr_tm':'DESC'})
        ret = []
        for project in projs:
            image = yield self.fetch(Images, project.image_id)
            project.get_image_url(image)
            ret.append(project)
        return ret

    def get_image_url(self, image):
        if image:
            self.__setattr__('image_url', image.image_url())
        else:
            self.__setattr__('image_url', '/static/img/' + 'projects' + '/' + \
                            'default.png')

class Experience(Main):

    __tablename__ = 'experience'
    _required_fields = ['title', 'subtitle', 'w_from']

    def __init__(self, user_id=None, title=None, subtitle=None, w_from=None, w_to=None, description=None):
        self.user_id = user_id
        self.title = title
        self.subtitle = subtitle
        self.w_from = w_from
        self.w_to = w_to
        self.description = description

    @tornado.gen.coroutine
    def save_experience(self, data):
        success = self.edit(data)
        if success == True:
            yield self.save()
            return self
        return success

    @tornado.gen.coroutine
    def edit_experience(self, data):
        success = self.edit(data)
        if success == True:
            yield self.update()
            return self
        return success

    def edit(self, data):
        frto = {'w_from':None, 'w_to': None}
        for k in self.__dict__:
            if k in data.keys():
                if k == 'w_from' or k == 'w_to':
                    frto[k] = strip_date(data[k])
                    if data[k]:
                        self.__setattr__(k, strip_date(data[k]))
                else:
                    self.__setattr__(k, data[k])
        if not self.check_date_frto(frto['w_from'], frto['w_to']):
            return 'Date is wrong!'
        return True

class Images(Main):

    __tablename__ = 'images'
    _required_fields = ['folder_name', 'file_name']

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
            self.mime = data['file']['mime']
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

class Visitors(Main):

    __tablename__ = 'visitors'
    _required_fields = []

    def __init__(self, location=None, last_visit=None, city=None, country=None, region=None, hostname=None, ip=None, count_visits=None):
        self.location = location
        self.last_visit = last_visit
        self.city = city
        self.country = country
        self.region = region
        self.hostname = hostname
        self.ip = ip
        self.count_visits = count_visits

    @tornado.gen.coroutine
    def save_visitors(self, ip):
        path = os.path.dirname(os.path.abspath('static')) + '/static/GeoLite2-City.mmdb'
        reader = geoip2.database.Reader(path)
        print(ip)
        try:
            response = reader.city(ip)
            yield self._save(response)
        except Exception as e:
            print(e)
        reader.close()

    @tornado.gen.coroutine
    def _save(self, georesp):
        region = parse.unquote(georesp.subdivisions.most_specific.name).replace('"', '_').replace('*', '_').replace('/', '_'). \
            replace('\\', '_').replace("'", '_')
        ip = str(georesp.traits.ip_address)
        visitor = yield self.fetch_by(Visitors, ip=ip)
        if visitor:
            visitor.last_visit = datetime.datetime.now()
            visitor.count_visits = visitor.count_visits + 1
            yield visitor.update()
        else:
            self.ip = georesp.traits.ip_address
            self.location = 'longitude: '+str(georesp.location.longitude)+' / '+'latitude: '+str(georesp.location.latitude)
            self.last_visit = datetime.datetime.now()
            self.city = georesp.city.name
            self.country = georesp.country.name
            self.region = region
            self.count_visits = 1
            yield self.save()