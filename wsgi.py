# from run import application
import tornado.ioloop
import tornado.web
import tornado.options
import tornado.httpserver
from psycopg2.extras import DictCursor
from urls import hundlers
import momoko
import config
from tornado.ioloop import IOLoop
from concurrent.futures import ThreadPoolExecutor
from handlers import ErrorHandler

class Application(tornado.web.Application):
    def __init__(self):
        _workers = ThreadPoolExecutor(max_workers=10)
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

        future = self.db.connect()
        ioloop.add_future(future, lambda x: ioloop.stop())
        ioloop.start()
        future.result()  # raises exception on connection error


def run():
    application = Application()
    application.listen(8080, config.HOST)
    tornado.ioloop.IOLoop.current().start()

application = run()