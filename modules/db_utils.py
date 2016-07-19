from tornado.ioloop import IOLoop
from psycopg2.extras import DictCursor
import momoko
import config

def db():
    ioloop = IOLoop.instance()
    db = momoko.Connection(dsn=config.DSN, cursor_factory=DictCursor)
    # self.log = Log('errors.log')
    try:
        future = db.connect()
        ioloop.add_future(future, lambda x: ioloop.stop())
        ioloop.start()
        future.result()
    except:
        pass
    return db