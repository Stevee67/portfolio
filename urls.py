from handlers import HomeHandler, AdminHandler, FormsHandler, EditPersonalInfo, EditSkills, Login, Logout, EditExperience, EditEducation

hundlers = [
            (r"/", HomeHandler),
            (r"/admin", AdminHandler),
            (r"/admin/forms", FormsHandler),
            (r"/admin/personal_info", EditPersonalInfo),
            (r"/admin/skills", EditSkills),
            (r"/admin/experience", EditExperience),
            (r"/admin/education", EditEducation),
            (r"/admin/login", Login),
            (r"/admin/logout", Logout),
        ]