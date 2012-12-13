from giotto.contrib.static.programs import StaticServe, SingleStaticServe
from giotto.programs import ProgramManifest, GiottoProgram, management_manifest
from giotto.views import JinjaTemplateView
from giotto.control import Redirection, M
from giotto.contrib.auth.middleware import (SetAuthenticationCookies, 
    AuthenticationMiddleware, LogoutMiddleware,
    NotAuthenticatedOrRedirect, AuthenticatedOrDie)
from giotto.contrib.auth.models import is_authenticated, basic_register

from config import project_path

from models import Blog

manifest = ProgramManifest({
    '': ProgramManifest({
        '': GiottoProgram(
            model=[Blog.all],
            view=JinjaTemplateView('blog_index.html', name="blogs"),
            controllers=('http-get', ),
        ),
        'blog': GiottoProgram(
            model=[Blog.get],
            view=JinjaTemplateView('blog.html'),
            controllers=('http-get', ),
        ),
        'new': [
            GiottoProgram(
                input_middleware=[AuthenticationMiddleware, AuthenticatedOrDie],
                view=JinjaTemplateView('new_blog.html'),
                controllers=('http-get', '*'),
            ),
            GiottoProgram(
                model=[Blog.create],
                view=Redirection("/blog", args=[M.id]),
                controllers = ('http-post', 'cmd'),
            ),
        ]
    }),
    'login': [
        GiottoProgram(
            input_middleware=[AuthenticationMiddleware, NotAuthenticatedOrRedirect('/')],
            controllers=('http-get',),
            view=JinjaTemplateView('login.html'),
        ),
        GiottoProgram(
            controllers=('http-post',),
            input_middleware=[AuthenticationMiddleware],
            model=[is_authenticated("Invalid username or password")],
            view=Redirection('/'),
            output_middleware=[SetAuthenticationCookies],
        ),
    ],
    'logout': GiottoProgram(
        view=Redirection('/'),
        output_middleware=[LogoutMiddleware],
    ),
    'register': [
        GiottoProgram(
            controllers=('http-get',),
            view=JinjaTemplateView('register.html')
        ),
        GiottoProgram(
            controllers=('http-post',),
            model=[basic_register],
            view=Redirection('/'),
            output_middleware=[SetAuthenticationCookies],
        ),

    ],
    'static': StaticServe(project_path + '/static/'),
    'favicon': SingleStaticServe('/Users/chris/Documents/favicon.ico'),
    'mgt': management_manifest,
})