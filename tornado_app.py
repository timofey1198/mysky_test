"""
С использованием Python 2 или 3 и фреймворка Tornado напишите веб-сервис со следующим функционалом

1. Логин и логаут пользователя
2. Только для залогиненных пользователей возможность загружать файлы PDF в сервис и смотреть уже загруженные
    в виде таблицы:  в первом столбце — логин пользователя, загрузившего файл; во втором — кликабельное
    имя файла, по клику на которое скачивается файл. (Достаточно сделать и загрузку, и список на одной странице.)
    Список отсортируйте по порядку загрузки файлов в сервис, начиная с самого раннего.
3. Загруженный в сервис PDF нужно разделить на отдельные страницы в формате PNG, которые вместе с исходным файлом
    должны также присутствовать в списке и скачиваться. Для рендеринга страниц из PDF можете использовать
    любой удобный модуль.
4. Если есть желание и время, то можете организовать "иерархию" файлов,
    чтобы каким-то образом была зафиксирована связь между
    PDF-файлом и созданными из него страницами.

В качестве базы данных используйте SQLite.
Вместе со ссылкой на код или кодом, напишите нам, как запускать ваш сервис.
"""

import tornado.web
import tornado.ioloop
import tornado.httpserver
import tornado.escape

from tornado.options import define, options, parse_command_line
import os.path
import sqlite3

import pdf


define("data_path", default="data.db", help="path to data base")
define("host", default="127.0.0.1", help="run on this host")
define("port", default=9999, help="run on the given port", type=int)
define("debug", default=False, help="run in debug mode")


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", MainHandler),
            (r"/login", LoginHandler),
            (r"/register", RegistrationHandler),
            (r"/download", DownloadHandler),
            (r"/upload", UploadHandler),
            (r"/logout", LogoutHandler),
        ]
        settings = dict(
            cookie_secret="__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            xsrf_cookies=True,
            debug=options.debug,
            login_url="/login",
        )
        super(Application, self).__init__(handlers, **settings)
        # База данных приложения
        self.db = sqlite3.connect(os.path.join(os.path.dirname(__file__), options.data_path))

        self._create_tables()

    def _create_tables(self):
        cursor = self.db.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS users (
                        id integer primary key AUTOINCREMENT NOT NULL,
                        login text,
                        password text)""")
        self.db.commit()
        cursor.execute("""CREATE TABLE IF NOT EXISTS documents (
                        id integer primary key AUTOINCREMENT NOT NULL,
                        file_name text,
                        owner text)""")
        self.db.commit()


class BaseHandler(tornado.web.RequestHandler):
    @property
    def db(self):
        return self.application.db

    def get_current_user(self):
        user_id = self.get_secure_cookie("user_id")
        if not user_id:
            return None
        cursor = self.db.cursor()
        cursor.execute("SELECT login FROM users WHERE id=?", (int(user_id),))
        login = cursor.fetchall()
        if login:
            return login[0][0]
        else:
            return None


class MainHandler(BaseHandler):
    @tornado.web.asynchronous
    def get(self, *args, **kwargs):
        if not self.get_current_user():
            self.render("index.html", content="", module="start.html")
        else:
            cursor = self.db.cursor()
            files = cursor.execute("SELECT * FROM documents").fetchall()
            self.render("index.html", content="Вы вошли!", module="files.html", files=files)


class LoginHandler(BaseHandler):
    def get(self, *args, **kwargs):
        self.render("index.html", content='', module="login.html")

    def post(self, *args, **kwargs):
        cursor = self.db.cursor()
        user_id = cursor.execute("SELECT id FROM users WHERE login=?",
                                 (self.get_argument("login"),)).fetchall()
        if user_id:
            self.set_secure_cookie("user_id", str(user_id[0][0]))
            self.redirect("/")
        else:
            self.redirect("/login")


class LogoutHandler(BaseHandler):
    def get(self, *args, **kwargs):
        self.set_secure_cookie("user_id", "")
        self.redirect("/")


class RegistrationHandler(BaseHandler):
    def get(self, *args, **kwargs):
        self.render("index.html", content='', module="registration.html")

    def post(self, *args, **kwargs):
        login = self.get_argument("login")
        password = self.get_argument("password")
        cursor = self.db.cursor()
        cursor.execute("INSERT INTO users VALUES (NULL, ?, ?)",
                       (login, password))
        self.db.commit()
        user_id = cursor.execute("SELECT id FROM users WHERE login=?",(login,)).fetchall()
        self.set_secure_cookie("user_id", str(user_id[0][0]))
        self.redirect("/")


class DownloadHandler(BaseHandler):
    def get(self):
        file_id = self.get_argument("file_id")
        file_name = self.get_argument("file_name")
        print(file_id)
        self.set_header('Content-Type', 'application/pdf')
        self.set_header('Content-Disposition', 'attachment; filename=%s' % file_name)
        self.flush()
        with open(os.path.join(os.path.dirname(__file__), "documents/{0}/{0}.pdf".format(file_id)), "rb") as f:
            self.finish(f.read())
        # self.redirect("/")


class UploadHandler(BaseHandler):
    def post(self):
        for field_name, files in self.request.files.items():
            for info in files:
                filename, content_type = info['filename'], info['content_type']
                print(filename, content_type)
                if content_type == "application/pdf":
                    cursor = self.db.cursor()
                    cursor.execute("INSERT INTO documents VALUES (NULL, ?, ?)",
                                   (filename, self.get_current_user()))
                    self.db.commit()
                    file_id = cursor.execute("SELECT COUNT(*) FROM documents").fetchall()[0][0]
                    pdf.save(file_id, info["body"], "documents")
        self.redirect("/")


def main():
    parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    # app = tornado.web.Application(
    #     [
    #         (r"/", MainHandler),
    #         (r"/login", LoginHandler),
    #         (r"/register", RegistrationHandler),
    #         (r"/download", DownloadHandler),
    #         (r"/upload", UploadHandler),
    #         (r"/logout", LogoutHandler),
    #     ],
    #     cookie_secret="__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",
    #     template_path=os.path.join(os.path.dirname(__file__), "templates"),
    #     static_path=os.path.join(os.path.dirname(__file__), "static"),
    #     xsrf_cookies=True,
    #     debug=options.debug,
    # )
    # app.listen(options.port)
    print("OK")
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()