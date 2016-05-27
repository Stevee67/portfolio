import os

PORT=8888
DSN="dbname='aboutme' user='webdev' password='webdev_access' " \
              "host=localhost port=5432"
TEMPLATE_PATH=os.path.join(os.path.dirname(__file__), "templates")
STATIC_PATH=os.path.join(os.path.dirname(__file__), "static")
MAIL_SERVER='smtp.gmail.com'
MAIL_PORT=587
MAIL_PASS = 'nokia532067'