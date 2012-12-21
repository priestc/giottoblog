from giotto.contrib.static.programs import StaticServe, SingleStaticServe
from giotto.programs import ProgramManifest, GiottoProgram, management_manifest
from giotto.views import jinja_template, BasicView
from giotto.control import Redirection, M
from giotto.contrib.auth.middleware import (PresentAuthenticationCredentials, 
    AuthenticationMiddleware, LogoutMiddleware,
    NotAuthenticatedOrRedirect, AuthenticatedOrDie)
from giotto.contrib.auth.models import is_authenticated, basic_register, create_session
from giotto.contrib.auth.views import LoginView

from config import project_path

from models import Blog, blog_index_mock, get_blog_mock, make_mock_blog

class AuthProgram(GiottoProgram):
    pre_input_middleware = [AuthenticationMiddleware]

manifest = ProgramManifest({
    '': ProgramManifest({
        '': AuthProgram(
            model=[Blog.all, blog_index_mock()],
            view=BasicView(
                html=jinja_template('html/blog_index.html'),
            ),
        ),
        'blog': AuthProgram(
            model=[Blog.get, get_blog_mock()],
            view=BasicView(
                html=jinja_template('html/blog.html'),
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
        model=[lambda x, y: {'x': x, 'y': y, 'result': int(x) * int(y)}],
        view=BasicView(),
    ),
    'login': [
        AuthProgram(
            input_middleware=[NotAuthenticatedOrRedirect('/')],
            view=BasicView(
                html=jinja_template('html/login.html'),
            ),
        ),
        AuthProgram(
            controllers=['http-post'],
            model=[create_session, {'username': 'mock_user', 'session_key': 'XXXXXXXXXXXXXXX'}],
            view=BasicView(
                html=lambda m: Redirection('/', persist={'giotto_session': m['session_key']}),
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