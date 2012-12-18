from giotto.contrib.static.programs import StaticServe, SingleStaticServe
from giotto.programs import ProgramManifest, GiottoProgram, management_manifest
from giotto.views import JinjaTemplateView, BasicView
from giotto.control import Redirection, M
from giotto.contrib.auth.middleware import (PresentAuthenticationCredentials, 
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
        ),
        'blog': AuthProgram(
            model=[Blog.get],
            view=JinjaTemplateView('html/blog.html'),
        ),
        'new': [
            AuthProgram(
                input_middleware=[AuthenticationMiddleware, AuthenticatedOrDie],
                view=JinjaTemplateView('html/blog_form.html'),
            ),
            AuthProgram(
                controllers = ('http-post', 'cmd'),
                model=[Blog.create],
                view=Redirection("/blog", args=[M.id]),
            ),
        ],
        'edit': [
            AuthProgram(
                model=[Blog.get],
                view=JinjaTemplateView('html/blog_form.html'),
            ),
            AuthProgram(
                controllers=('http-post', 'cmd'),
                model=[Blog.edit],
                view=Redirection('/blog', args=[M.id]),
            )
        ]
    }),
    'multiply': GiottoProgram(
        model=[lambda x, y: {'x': x, 'y': y, 'result': int(x) * int(y)}],
        view=BasicView,
    ),
    'login': [
        AuthProgram(
            input_middleware=[NotAuthenticatedOrRedirect('/')],
            view=JinjaTemplateView('html/login.html'),
        ),
        AuthProgram(
            controllers=('http-post',),
            input_middleware=[AuthenticationMiddleware],
            model=[is_authenticated("Invalid username or password")],
            view=Redirection('/'),
            output_middleware=[PresentAuthenticationCredentials],
        ),
    ],
    'logout': AuthProgram(
        view=Redirection('/'),
        output_middleware=[LogoutMiddleware],
    ),
    'register': [
        AuthProgram(
            input_middleware=[NotAuthenticatedOrRedirect('/')],
            view=JinjaTemplateView('html/register.html')
        ),
        AuthProgram(
            controllers=('http-post',),
            model=[basic_register],
            view=Redirection('/'),
            output_middleware=[PresentAuthenticationCredentials],
        ),

    ],
    'static': StaticServe(project_path + '/static/'),
    'favicon': SingleStaticServe('favicon.ico'),
    'mgt': management_manifest,
})