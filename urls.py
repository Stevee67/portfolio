from handlers import HomeHandler, AdminHandler, FormsHandler, EditPersonalInfo, EditSkills, Login, Logout, EditExperience

hundlers = [
            (r"/", HomeHandler),
            (r"/admin", AdminHandler),
            (r"/admin/forms", FormsHandler),
            (r"/admin/personal_info", EditPersonalInfo),
            (r"/admin/skills", EditSkills),
            (r"/admin/experience", EditExperience),
            (r"/admin/login", Login),
            (r"/admin/logout", Logout),
        ]