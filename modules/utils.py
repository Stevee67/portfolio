import datetime
import time
import tornado.gen
import smtplib
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


def send_message(message):
    to = 'stopa6767@gmail.com'
    gmail_user = 'stopa6767@gmail.com'
    gmail_pwd = 'nokia675320'
    smtpserver = smtplib.SMTP("smtp.gmail.com", 587)
    smtpserver.ehlo()
    smtpserver.starttls()
    smtpserver.ehlo
    smtpserver.login(gmail_user, gmail_pwd)
    header = 'To:' + to + '\n' + 'From: ' + gmail_user + '\n' + 'Subject:testing \n'
    msg = header + '\n '+message+'\n\n'
    smtpserver.sendmail(gmail_user, to, msg)
    smtpserver.close()
