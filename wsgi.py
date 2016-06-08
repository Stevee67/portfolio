from run import application
import tornado.wsgi
application = tornado.wsgi.WSGIAdapter(application)
