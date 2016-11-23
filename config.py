import os

TEMPLATE_PATH=os.path.join(os.path.dirname(__file__), "templates")
STATIC_PATH=os.path.join(os.path.dirname(__file__), "static")
MAIL_SERVER='smtp.gmail.com'
MAIL_PORT='587'
MAIL_PASS = ''
SENDER_ADDRESS = ''
SECRET_COOKIE = ''
DEFAULT_IMAGE_ID = '0000000-0000-0000-0000-000000000001'
LIMIT_MESSAGES = 3

DB_HOST = ''
DB_USER = ''
DB_PASS = ''
DB_NAME = ''
DB_PORT = 5432
if os.environ.get('OPENSHIFT_REPO_DIR'):
    DB_USER = os.environ.get('OPENSHIFT_POSTGRESQL_DB_USERNAME')
    DB_HOST = os.environ.get('OPENSHIFT_POSTGRESQL_DB_HOST')
    DB_PASS = os.environ.get('OPENSHIFT_POSTGRESQL_DB_PASSWORD')
    DB_PORT = os.environ.get('OPENSHIFT_POSTGRESQL_DB_PORT')

PORT = os.environ.get('OPENSHIFT_PYTHON_PORT') or 8000
HOST = os.environ.get('OPENSHIFT_PYTHON_IP') or '0.0.0.0'

DSN = "dbname='{}' user='{}' password='{}' " \
      "host='{}' port={}".format(DB_NAME, DB_USER, DB_PASS, DB_HOST, DB_PORT)