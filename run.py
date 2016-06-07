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

def run():
    aplication = Application()
    aplication.listen(8888, '0.0.0.0')
    tornado.ioloop.IOLoop.current().start()

class Application(tornado.web.Application):
    def __init__(self):
        _workers = ThreadPoolExecutor(max_workers=10)
        handlers = hundlers
        settings = dict(
            portfolio_title=u"Stepan Shysh",
            template_path=config.TEMPLATE_PATH,
            static_path=config.STATIC_PATH,
            cookie_secret=config.SECRET_COOKIE,
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




        # self.db = momoko.Pool(url, size=5)
        # future = self.db.connect()
        # ioloop.add_future(future, lambda x: ioloop.stop())
        # ioloop.start()
        # future.result()
        # Have one global connection to the blog DB across all handlers
        # self.db = torndb.Connection(
        #     host=options.mysql_host, database=options.mysql_database,
        #     user=options.mysql_user, password=options.mysql_password)
        #
        # self.maybe_create_tables()

    # def maybe_create_tables(self):
    #     try:
    #         self.db.get("SELECT COUNT(*) from entries;")
    #     except MySQLdb.ProgrammingError:
    #         subprocess.check_call(['mysql',
    #                                '--host=' + options.mysql_host,
    #                                '--database=' + options.mysql_database,
    #                                '--user=' + options.mysql_user,
    #                                '--password=' + options.mysql_password],
    #                               stdin=open('schema.sql'))


if __name__ == "__main__":
    run()