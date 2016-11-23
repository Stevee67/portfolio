import datetime
import threading
import time
import config
import smtplib
import tornado.gen
import math
import logging


def datetime_from_utc_to_local(utc_datetime):
    now_timestamp = time.time()
    offset = datetime.datetime.fromtimestamp(now_timestamp) - datetime.datetime.utcfromtimestamp(now_timestamp)
    return utc_datetime + offset


def format_date(date):
    b = datetime_from_utc_to_local(date)
    month = b.month if len(str(b.month)) > 1 else '0'+str(b.month)
    day = b.day if len(str(b.day)) > 1 else '0'+str(b.day)
    formating_date = '{0}/{1}/{2}'.format(month, day, b.year)
    return formating_date


def strip_date(date):
    if date:
        return datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%S.%fZ')
    else:
        return None


def send_message(message, password=config.MAIL_PASS):
    fromaddr = config.SENDER_ADDRESS
    toaddrs = config.SENDER_ADDRESS
    message = 'Subject: New email from my PORTFOLIO\n\n' + message
    username = config.SENDER_ADDRESS
    server = smtplib.SMTP(config.MAIL_SERVER+':'+config.MAIL_PORT)
    server.starttls()
    server.login(username, password)
    server.sendmail(fromaddr, toaddrs, message)
    server.quit()


@tornado.gen.coroutine
def send_message_async(message):
    yield call_blocking_func(send_message, message)


@tornado.gen.coroutine
def call_blocking_func(func, *args, **kwargs):
    threading.Thread(target=func, args=args, kwargs=kwargs).start()


@tornado.gen.coroutine
def dict_from_cursor_one(curso):
    cursor = yield curso
    keys = cursor.description
    obj = cursor.fetchone()
    new_dict = {}
    if obj:
        for k in keys:
            if isinstance(obj[k[0]], datetime.datetime):
                new_dict[k[0]] = format_date(obj[k[0]])
            else:
                new_dict[k[0]] = obj[k[0]]
        return new_dict


def object_to_dict(object):
    new_dict = {}
    if object:
        for k in object.__dict__:
            if isinstance(object.__getattribute__(k), datetime.datetime):
                new_dict[k] = format_date(object.__getattribute__(k))
            else:
                new_dict[k] = object.__getattribute__(k)
        return new_dict


def dict_from_cursor_all(cursor):
    keys = cursor.description
    objs = cursor.fetchall()
    list_objs = []
    for obj in objs:
        if obj:
            new_dict = {}
            for k in keys:
                if k[0] != 'password_hash':
                    if isinstance(obj[k[0]], datetime.datetime):
                        new_dict[k[0]] = format_date(obj[k[0]])
                    else:
                        new_dict[k[0]] = obj[k[0]]
            list_objs.append(new_dict)
    return list_objs


def merge_dict(list_dict):
    new_dict = {}
    for d in list_dict:
        new_dict.update(d)
    return new_dict


def merge_object_by_kk(list_dict, k1, k2):
    new_dict = {}
    for el in list_dict:
        new_dict[el.__getattribute__(k1)] = el.__getattribute__(k2)
    return new_dict


@tornado.gen.coroutine
def pagination(db, table, item_per_page, page, order_by):
    cur_count = yield db.execute("SELECT COUNT(id) FROM {}".format(table))
    len = cur_count.fetchone()
    pages = len[0]/item_per_page
    offset = (page-1) * item_per_page
    SQL = "SELECT * FROM {0}".format(table)
    if order_by:
        SQL += ' ORDER BY'
        for ok, ov in order_by.items():
            SQL += ' {} {},'.format(ok, ov)
        SQL = SQL[0:-1]
    SQL += " LIMIT {0} OFFSET {1}".format(
             item_per_page, offset)
    data = yield db.execute(SQL)
    return math.ceil(pages), dict_from_cursor_all(data), len[0]


class Log:
    def __init__(self, path):
        logging.basicConfig(format=u'%(levelname)-8s [%(asctime)s] %(message)s',
                            filename=path, level=logging.DEBUG)
    @staticmethod
    def error(message):
        logging.error(message)
        print(message)


def success(func):
    @tornado.gen.coroutine
    def wrapped(obj,*args, **kwargs):
        result = yield func(obj,*args, **kwargs)
        if isinstance(result, dict):
            res = {'dict_data': result, 'error': 'false', 'success': 'true'}
        elif isinstance(result, str):
            res = {'data': {}, 'error': result, 'success': 'false'}
        elif isinstance(result, list):
            data = []
            for d in result:
                if isinstance(d, str):
                    data.append(d)
                else:
                    data.append(object_to_dict(d))
            res =  {'data': data,'error': 'false', 'success': 'true'}
        else:
            res = {'data': object_to_dict(result), 'error': 'false', 'success': 'true'}
        obj.write(res)
        obj.finish()
    return wrapped






