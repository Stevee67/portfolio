from handlers import HomeHandler, AdminHandler, FormsHandler, EditPersonalInfo, EditSkills, Login, Logout

hundlers = [
            (r"/", HomeHandler),
            (r"/admin", AdminHandler),
            (r"/admin/forms", FormsHandler),
            (r"/admin/personal_info", EditPersonalInfo),
            (r"/admin/skills", EditSkills),
            (r"/admin/login", Login),
            (r"/admin/logout", Logout),
        ]