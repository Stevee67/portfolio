import datetime
import time
import tornado.gen

def datetime_from_utc_to_local(utc_datetime):
    now_timestamp = time.time()
    offset = datetime.datetime.fromtimestamp(now_timestamp) - datetime.datetime.utcfromtimestamp(now_timestamp)
    return utc_datetime + offset

def format_date(date):
    # d = datetime.datetime.strptime(str(date), "%Y-%m-%dT%H:%M:%S%Z")
    b = datetime_from_utc_to_local(date)
    month = b.month if len(str(b.month)) > 1 else '0'+str(b.month)
    formating_date = '{0}-{1}-{2}'.format(b.day, month, b.year)
    return formating_date
