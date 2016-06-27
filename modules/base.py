import tornado.web, tornado.gen
import datetime
from urllib import parse
from modules.utils import dict_from_cursor_one
from modules.db_utils import db

db = db()

class BaseHandler(tornado.web.RequestHandler):


    @property
    def log(self):
        return self.application.log

    @property
    def db(self):
        # if db.closed:
        #     db.connect()
        return db

    @tornado.gen.coroutine
    def prepare(self):
        yield db.connect()
        return super(BaseHandler, self).prepare()

    @tornado.gen.coroutine
    def on_finish(self):
        if not self.db.closed:
            self.db.close()
        return super(BaseHandler, self).on_finish()

class Base(BaseHandler):

    @tornado.gen.coroutine
    def fetch(self, Module, id, filter_by=None):
        """
        :param Module: class for object that we return
        :param id: get object by id
        :param filter_by:  attribute is dict where key - field in Module.__tablename__ and value - value for this field
        :return Module object:
        """
        SQL = "SELECT * FROM {0} WHERE id='{1}'".format(Module.__tablename__, id)
        if filter_by:
            if not isinstance(filter_by, dict):
                raise AttributeError('The filter_by attribute must be dictionary!')
            SQL += ' AND'
            for fk, fv in filter_by.items():
                SQL += " {0}='{1}' AND ".format(fk, fv)
            SQL = SQL[0:-4]
        cur = yield self.db.execute(SQL)
        return Module.get(cur)

    @tornado.gen.coroutine
    def fetch_all(self, Module, filter_by=None, order_by=None):
        """
            :param Module: class for list objects that we return
            :param filter_by:  attribute is dict where key - field in Module.__tablename__ and value - value for this field
            :param order_by: attribute is dict where key 'field' - field in which we will sort
                   and 'type' - DESC or ASC sorted type
            :return list Module objects:
        """
        SQL = "SELECT * FROM {0}".format(Module.__tablename__)
        if filter_by:
            if not isinstance(filter_by, dict):
                raise AttributeError('The filter_by attribute must be dictionary!')
            SQL += ' WHERE'
            for fk, fv in filter_by.items():
                SQL += " {0}='{1}' AND ".format(fk, fv)
            SQL = SQL[0:-4]
        if order_by:
            if not isinstance(order_by, dict):
                raise AttributeError('The sort_by attribute must be dictionary!')
            SQL += ' ORDER BY {} {}'.format(order_by['field'], order_by['type'])
        cur = yield self.db.execute(SQL)
        return Module.get_all(cur)

    @tornado.gen.coroutine
    def fetch_by(self, Module, **kwargs):
        SQL = "SELECT * FROM {} WHERE ".format(Module.__tablename__)
        for k, v in kwargs.items():
            SQL += "{0}='{1}' AND ".format(k, v)
        SQL = SQL[0:-4]
        cur = yield self.db.execute(SQL)
        return Module.get(cur)

    @tornado.gen.coroutine
    def save(self):
        if not self.check_required_fields():
            return
        SELECT_SQL = 'SELECT * FROM {}'.format(self.__class__.__dict__['__tablename__'])+ ' WHERE '
        SQL_INSERT = "INSERT INTO {} (".format(self.__class__.__dict__['__tablename__'])
        VALUES = ' VALUES('
        for k in self.__dict__:
            if self.__getattribute__(k) != None:
                SQL_INSERT += "{},".format(k)
                SELECT_SQL +="{0}='{1}' AND ".format(k, self.__getattribute__(k))
                VALUES += "'{}',".format(self.__getattribute__(k))
        SQL = SQL_INSERT[0:-1]+ ')' + VALUES[0:-1]+')'
        yield self.db.execute(SQL)
        cur_select = yield self.db.execute(SELECT_SQL[0:-4])
        result = self.__class__.get(cur_select)
        self.id = result.id

    @tornado.gen.coroutine
    def update(self, filter=None):
        """
        :param filter: must be dict with field and value key
        :return:
        """
        if not self.check_required_fields():
            return
        SQL_UPDATE = "UPDATE {} SET ".format(self.__class__.__dict__['__tablename__'])
        for k in self.__dict__:
            if k != 'id' and self.__getattribute__(k) != None:
                SQL_UPDATE += "{}='{}',".format(k, self.__getattribute__(k))
        if not filter:
            SQL = SQL_UPDATE[0:-1] + " WHERE id='{}'".format(self.id)
        else:
            SQL = SQL_UPDATE[0:-1] + " WHERE {field}='{value}'".format(**filter)
        yield self.db.execute(SQL)


    @tornado.gen.coroutine
    def remove(self):
        yield self.db.execute("DELETE FROM {} WHERE id='{}'".format(self.__class__.__dict__['__tablename__'], self.id))

    @classmethod
    def get(cls, cursor):
        obj = cursor.fetchone()
        object = cls()
        if obj:
            for k in object.__dict__.keys():
                if k in obj:
                    object.__setattr__(k, obj[k])
                else:
                    object.__setattr__(k, None)
            if 'id' in obj:
                object.__setattr__('id', obj['id'])
            return object

    @classmethod
    def get_all(cls, cursor):
        objs = cursor.fetchall()
        list_objs = []
        for obj in objs:
            object = cls()
            keys = object.__dict__.keys()
            if obj:
                for k in keys:
                    if k in obj:
                        object.__setattr__(k, obj[k])
                    else:
                        object.__setattr__(k, None)
                if 'id' in obj:
                    object.__setattr__('id', obj['id'])
                list_objs.append(object)
        return list_objs

    def get_current_user(self):
        return self.get_secure_cookie("email")

    @tornado.gen.coroutine
    def save_visitors(self, data):
        region = parse.unquote(data['region']).replace('"', '_').replace('*', '_').replace('/', '_'). \
            replace('\\', '_').replace("'", '_')
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
