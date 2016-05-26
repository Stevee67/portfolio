import tornado.web
import tornado.gen
from modules.utils import format_date

class BaseHandler(tornado.web.RequestHandler):
    @property
    def db(self):
        return self.application.db

    @property
    def db_connect(self):
        return self.application.db_connect

    def get_current_user(self):
        user_id = '984e586d-bd84-4ecc-b261-46b1c9c00c8c'
        if not user_id: return None
        return  self.db.execute("SELECT * FROM personal_info WHERE id = '{}'".format(user_id))
    #
    # def any_author_exists(self):
    #     return bool(self.db.get("SELECT * FROM authors LIMIT 1"))


class HomeHandler(BaseHandler):

    @tornado.gen.coroutine
    def get(self):
        user = yield self.db.execute("SELECT * FROM personal_info")
        skills = yield self.db.execute("SELECT * FROM skils ORDER BY kn_percent DESC")
        experiences = yield self.db.execute("SELECT * FROM experience")
        educations = yield self.db.execute("SELECT * FROM educations")
        projects = yield self.db.execute("SELECT * FROM projects")
        # entries = self.db.query("SELECT * FROM entries ORDER BY published "
        #                         "DESC LIMIT 5")
        # if not entries:
        #     self.redirect("/compose")
        #     return
        # print(user.fetchone())
        current_user = yield self.get_current_user()
        self.current_user = current_user.fetchone()
        self.render("index.html", user=user.fetchone(),
                                  skills=skills.fetchall(),
                                  experiences=experiences.fetchall(),
                                  educations=educations,
                                  projects=projects,
                                  format_date=format_date)

