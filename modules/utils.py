import datetime
import threading
import time
import config
import smtplib
import tornado.gen


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
def call_blocking_func(func, *args):
    threading.Thread(target=func, args=args).start()