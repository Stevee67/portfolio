from handlers import HomeHandler, AdminHandler, FormsHandler, EditPersonalInfo, EditSkills, Login, Logout, \
    EditExperience, EditEducation, EditProjects, EditStaticData, Visitors

hundlers = [
            (r"/", HomeHandler),
            (r"/admin", AdminHandler),
            (r"/admin/forms", FormsHandler),
            (r"/admin/personal_info", EditPersonalInfo),
            (r"/admin/skills", EditSkills),
            (r"/admin/experience", EditExperience),
            (r"/admin/education", EditEducation),
            (r"/admin/projects", EditProjects),
            (r"/admin/static", EditStaticData),
            (r"/admin/visitors", Visitors),
            (r"/admin/login", Login),
            (r"/admin/logout", Logout),
        ]