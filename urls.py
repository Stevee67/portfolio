from handlers import HomeHandler, AdminHandler, FormsHandler, EditPersonalInfo, EditSkills

hundlers = [
            (r"/", HomeHandler),
            (r"/admin", AdminHandler),
            (r"/admin/forms", FormsHandler),
            (r"/admin/personal_info", EditPersonalInfo),
            (r"/admin/skills", EditSkills),
        ]