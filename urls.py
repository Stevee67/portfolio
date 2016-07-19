from handlers import HomeHandler, AdminHandler, EditPersonalInfo, EditSkills, Login, Logout, \
    EditExperience, EditEducation, EditProjects, EditStaticData, ListVisitors

hundlers = [
            (r"/", HomeHandler),
            (r"/admin", AdminHandler),
            (r"/admin/personal_info", EditPersonalInfo),
            (r"/admin/skills", EditSkills),
            (r"/admin/experience", EditExperience),
            (r"/admin/education", EditEducation),
            (r"/admin/projects", EditProjects),
            (r"/admin/static", EditStaticData),
            (r"/admin/visitors", ListVisitors),
            (r"/admin/login", Login),
            (r"/admin/logout", Logout),
        ]