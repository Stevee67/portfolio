import datetime
import threading
import time
import config
import smtplib
import tornado.gen
from werkzeug.security import generate_password_hash, check_password_hash

def datetime_from_utc_to_local(utc_datetime):
    now_timestamp = time.time()
    offset = datetime.datetime.fromtimestamp(now_timestamp) - datetime.datetime.utcfromtimestamp(now_timestamp)
    return utc_datetime + offset

def format_date(date):
    b = datetime_from_utc_to_local(date)
    month = b.month if len(str(b.month)) > 1 else '0'+str(b.month)
    formating_date = '{0}-{1}-{2}'.format(b.day, month, b.year)
    return formating_date

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
    for k in keys:
        if k[0] != 'password_hash':
            new_dict[k[0]] = obj[k[0]]
    return new_dict

def dict_from_cursor_all(cursor):
    keys = cursor.description
    objs = cursor.fetchall()
    list_objs = []
    for obj in objs:
        new_dict = {}
        for k in keys:
            if k[0] != 'password_hash':
                new_dict[k[0]] = obj[k[0]]
        list_objs.append(new_dict)
    return list_objs


def generate_password(password):
    if password:
           return generate_password_hash(password,
                                   method='pbkdf2:sha256',
                                   salt_length=32)

def verify_password(pwhash, password):
    return pwhash and \
           check_password_hash(pwhash, password)
