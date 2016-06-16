import datetime
import threading
import time
import config
import smtplib
import tornado.gen
from werkzeug.security import generate_password_hash, check_password_hash
from os import listdir
from os.path import isfile, join
import re
import math
import logging

def get_only_files_from_dir(path):
    return [f for f in listdir(path) if isfile(join(path, f))]

def get_next_index_from_file(path):
    files = get_only_files_from_dir(path)
    index = 1
    for file in files:
        reg = re.match('([a-z_-]*[0-9_-]*)+(\((\d)+\))+\.\w+', file)
        if reg:
            if int(reg.group(3)) > index:
                index = int(reg.group(3))+1
    return index



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

def dict_from_cursor_one(cursor):
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

def merge_dict_by_kk(list_dict, k1, k2):
    new_dict = {}
    for el in list_dict:
        new_dict[el[k1]] = el[k2]
    return new_dict

def generate_password(password):
    if password:
           return generate_password_hash(password,
                                   method='pbkdf2:sha256',
                                   salt_length=32)

def verify_password(pwhash, password):
    return pwhash and \
           check_password_hash(pwhash, password)

@tornado.gen.coroutine
def paginaion(db, table, item_per_page, page):
    cur_pages = yield db.execute("SELECT COUNT(ip) FROM {}".format(table))
    len = cur_pages.fetchone()
    pages = len[0]/item_per_page
    offset = (page-1) * item_per_page
    data = yield db.execute("SELECT * FROM {0} LIMIT {1} OFFSET {2}"
                                     .format(table, item_per_page, offset))
    return math.ceil(pages), dict_from_cursor_all(data)


class Log:
    def __init__(self, path):
        logging.basicConfig(format=u'%(levelname)-8s [%(asctime)s] %(message)s',
                            filename=path, level=logging.DEBUG)
    @staticmethod
    def error(message):
        logging.error(message)
        print(message)







