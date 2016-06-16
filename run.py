import tornado.ioloop
import tornado.web
import tornado.options
import tornado.httpserver
from psycopg2.extras import DictCursor
from urls import hundlers
import momoko
import config
from tornado.ioloop import IOLoop
from handlers import ErrorHandler
from modules.utils import Log
import tornado.wsgi

class Application(tornado.web.Application):
    def __init__(self):
        handlers = hundlers
        settings = dict(
            portfolio_title=u"Stepan Shysh",
            template_path=config.TEMPLATE_PATH,
            static_path=config.STATIC_PATH,
            cookie_secret=config.SECRET_COOKIE,
            default_handler_class=ErrorHandler,
            default_handler_args= dict(status_code=404),
            login_url="/auth/login",
            debug=True,
        )
        super(Application, self).__init__(handlers, **settings)
        ioloop = IOLoop.instance()

        self.db = momoko.Connection(dsn=config.DSN, cursor_factory=DictCursor)
        self.log = Log('errors.log')
        try:
            future = self.db.connect()
            ioloop.add_future(future, lambda x: ioloop.stop())
            ioloop.start()
            future.result()
        except:
            self.log.error('Error db conection!')
          # raises exception on connection error

application = Application()
def run():
    container = tornado.wsgi.WSGIContainer(application)
    http_server = tornado.httpserver.HTTPServer(container)
    print(config.PORT, config.HOST)
    http_server.listen(config.PORT, config.HOST)
    tornado.ioloop.IOLoop.current().start()

if __name__ == "__main__":
    run()