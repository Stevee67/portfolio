import tornado.ioloop
import tornado.web
import tornado.options
import tornado.httpserver
from urls import hundlers
import config
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
            # self.log.error('Error db conection!')
          # raises exception on connection error


application = Application()
def run():
    server = tornado.httpserver.HTTPServer(application, no_keep_alive=True, xheaders=True)
    server.listen(config.PORT, config.HOST)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    run()