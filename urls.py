from handlers import HomeHandler, AdminHandler, FormsHandler, EditPersonalInfo

hundlers = [
            (r"/", HomeHandler),
            (r"/admin", AdminHandler),
            (r"/admin/forms", FormsHandler),
            (r"/admin/personal_info", EditPersonalInfo),
        ]