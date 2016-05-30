from handlers import HomeHandler

hundlers = [
            (r"/", HomeHandler),
            # (r"/archive", ArchiveHandler),
            # (r"/feed", FeedHandler),
            # (r"/entry/([^/]+)", EntryHandler),
            # (r"/compose", ComposeHandler),
            # (r"/auth/create", AuthCreateHandler),
            # (r"/auth/login", AuthLoginHandler),
            # (r"/auth/logout", AuthLogoutHandler),
        ]