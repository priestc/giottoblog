from giotto.contrib.static.programs import StaticServe, SingleStaticServe
from giotto.programs import ProgramManifest, GiottoProgram
from giotto.programs.management import management_manifest
from giotto.views import jinja_template, BasicView, partial_jinja_template, lazy_jinja_template
from giotto.control import Redirection
from giotto.contrib.auth.middleware import (AuthenticationMiddleware, LogoutMiddleware,
    NotAuthenticatedOrRedirect, AuthenticatedOrDie, NotAuthenticatedOrDie)
from giotto.contrib.auth.models import basic_register, create_session
from giotto.contrib.auth.views import LoginView
#from giotto.contrib.messages.middleware import AppendMessages
from giotto.middleware import RenderLazytemplate

from config import project_path

from models import Blog, blog_index_mock, get_blog_mock, make_mock_blog

class AuthProgram(GiottoProgram):
    pre_input_middleware = [AuthenticationMiddleware]

manifest = ProgramManifest({
    '': ProgramManifest({
        '': AuthProgram(
            model=[Blog.all, blog_index_mock()],
            view=BasicView(
                html=lazy_jinja_template('html/blog_index.html'),
            ),
            output_middleware=[RenderLazytemplate]
        ),
        'blog': AuthProgram(
            model=[Blog.get, get_blog_mock()],
            view=BasicView(
                html=partial_jinja_template('html/blog.html'),
            ),
        ),
        'new': [
            AuthProgram(
                input_middleware=[AuthenticatedOrDie],
                view=BasicView(
                    html=jinja_template('html/blog_form.html'),
                ),
            ),
            AuthProgram(
                input_middleware=[AuthenticatedOrDie],
                controllers = ('http-post', 'cmd'),
                model=[Blog.create, make_mock_blog()],
                view=BasicView(
                    html=lambda m: Redirection("/blog/%s" % m.id),
                ),
            ),
        ],
        'edit': [
            AuthProgram(
                model=[Blog.get],
                view=BasicView(
                    html=jinja_template('html/blog_form.html'),
                ),
            ),
            AuthProgram(
                controllers=['http-post', 'cmd'],
                model=[Blog.edit],
                view=BasicView(
                    html=lambda m: Redirection('/blog/%s' % m.id),
                ),
            ),
        ],
    }),
    'multiply': GiottoProgram(
        model=[lambda x, y: {'x': x, 'y': y, 'result': int(x) * int(y)}, {'a': [1,2,3,4,5]}],
        view=BasicView(
            irc=lambda m: "\x0302%(x)s\x03 * \x0302%(y)s\x03 == \x0304%(result)s\x03" % m
        ),
    ),
    'login': [
        AuthProgram(
            input_middleware=[NotAuthenticatedOrRedirect('/')],
            view=BasicView(
                html=jinja_template('html/login.html'),
            ),
        ),
        AuthProgram(
            input_middleware=[NotAuthenticatedOrDie],
            controllers=['http-post', 'cmd'],
            model=[create_session, {'username': 'mock_user', 'session_key': 'XXXXXXXXXXXXXXX'}],
            view=BasicView(
                persist=lambda m: {'giotto_session': m['session_key']},
                html=lambda m: Redirection('/'),
            ),
        ),
    ],
    'logout': AuthProgram(
        view=BasicView(
            html=Redirection('/'),
        ),
        output_middleware=[LogoutMiddleware],
    ),
    'register': [
        AuthProgram(
            input_middleware=[NotAuthenticatedOrRedirect('/')],
            view=BasicView(
                html=jinja_template('html/register.html'),
            ),
        ),
        AuthProgram(
            controllers=['http-post'],
            model=[basic_register],
            view=BasicView(
                html=lambda m: Redirection('/', persist={'giotto_session': m['session_key']}),
            ),
        ),
    ],
    'static': StaticServe(project_path + '/static/'),
    'favicon': SingleStaticServe('favicon.ico'),
    'mgt': management_manifest,
})