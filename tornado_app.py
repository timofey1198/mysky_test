import tornado.web
import tornado.ioloop

from tornado.options import define, options, parse_command_line
import os.path
import sqlite3


define("data_path", default="data.db", help="path to data base")
define("host", default="127.0.0.1", help="run on this host")
define("port", default=8888, help="run on the given port", type=int)
define("debug", default=False, help="run in debug mode")


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [

        ]
        settings = dict(

        )
        super(Application, self).__init__(handlers, **settings)
        # База данных приложения
        self.db = sqlite3.connect(os.path.join(os.path.dirname(__file__), options.data_path))

        self._create_tables()

    def _create_tables(self):
        cursor = self.db.cursor()
        try:
            cursor.execute("SELECT COUNT(*) FROM users")
        except:
            cursor.execute("""CREATE TABLE users (
                            id integer primary key,
                            login text,
                            password text)""")
        try:
            cursor.execute("SELECT COUNT(*) FROM documents")
        except:
            cursor.execute("""CREATE TABLE documents (
                            id integer primary key,
                            file_name text,
                            owner text)""")


class MainHandler(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        self.render("index.html", content="bjhjjlkmlm")


class LoginHandler(tornado.web.RequestHandler):
    def __init__(self):
        pass


class LogoutHandler(tornado.web.RequestHandler):
    def __init__(self):
        pass


class RegistrationHandler(tornado.web.RequestHandler):
    def __init__(self):
        pass


class DownloadHandler(tornado.web.RequestHandler):
    def __init__(self):
        pass


class UploadHandler(tornado.web.RequestHandler):
    def __init__(self):
        pass


def main():
    parse_command_line()
    app = tornado.web.Application(
        [
            (r"/", MainHandler),
            (r"/login", LoginHandler),
            (r"/register", RegistrationHandler),
            (r"/download", DownloadHandler),
            (r"/upload", UploadHandler),
            (r"/logout", LogoutHandler),
        ],
        cookie_secret="__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",
        template_path=os.path.join(os.path.dirname(__file__), "templates"),
        static_path=os.path.join(os.path.dirname(__file__), "static"),
        xsrf_cookies=True,
        debug=options.debug,
    )
    app.listen(options.port)
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()