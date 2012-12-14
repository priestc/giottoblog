from giotto.contrib.static.programs import StaticServe, SingleStaticServe
from giotto.programs import ProgramManifest, GiottoProgram, management_manifest
from giotto.views import JinjaTemplateView, BasicView
from giotto.control import Redirection, M
from giotto.contrib.auth.middleware import (SetAuthenticationCookies, 
    AuthenticationMiddleware, LogoutMiddleware,
    NotAuthenticatedOrRedirect, AuthenticatedOrDie)
from giotto.contrib.auth.models import is_authenticated, basic_register

from config import project_path

from models import Blog

class AuthProgram(GiottoProgram):
    pre_input_middleware = [AuthenticationMiddleware]

manifest = ProgramManifest({
    '': ProgramManifest({
        '': AuthProgram(
            model=[Blog.all],
            view=JinjaTemplateView('html/blog_index.html'),
            controllers=('http-get', ),
        ),
        'blog': AuthProgram(
            model=[Blog.get],
            view=JinjaTemplateView('html/blog.html'),
            controllers=('http-get', ),
        ),
        'new': [
            AuthProgram(
                input_middleware=[AuthenticationMiddleware, AuthenticatedOrDie],
                view=JinjaTemplateView('html/new_blog.html'),
                controllers=('http-get', '*'),
            ),
            AuthProgram(
                model=[Blog.create],
                view=Redirection("/blog", args=[M.id]),
                controllers = ('http-post', 'cmd'),
            ),
        ]
    }),
    'multiply': GiottoProgram(
        model=[lambda x, y: {'x': x, 'y': y, 'result': int(x) * int(y)}],
        view=BasicView,
    ),
    'login': [
        AuthProgram(
            input_middleware=[AuthenticationMiddleware, NotAuthenticatedOrRedirect('/')],
            controllers=('http-get',),
            view=JinjaTemplateView('html/login.html'),
        ),
        AuthProgram(
            controllers=('http-post',),
            input_middleware=[AuthenticationMiddleware],
            model=[is_authenticated("Invalid username or password")],
            view=Redirection('/'),
            output_middleware=[SetAuthenticationCookies],
        ),
    ],
    'logout': AuthProgram(
        view=Redirection('/'),
        output_middleware=[LogoutMiddleware],
    ),
    'register': [
        AuthProgram(
            input_middleware=[AuthenticationMiddleware, NotAuthenticatedOrRedirect('/')],
            controllers=('http-get',),
            view=JinjaTemplateView('html/register.html')
        ),
        AuthProgram(
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