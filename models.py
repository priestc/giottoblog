from giotto.exceptions import InvalidInput, DataNotFound
from giotto.contrib.auth.models import User
from giotto.primitives import LOGGED_IN_USER

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from giotto import config 

class Blog(config.Base):
    """
    Represents a user who has a blog repo
    """
    id = Column(Integer, primary_key=True)
    
    author_id = Column(Integer, ForeignKey('giotto_user.username'))
    author = relationship("User", backref=backref('blogs', order_by=id))

    title = Column(String)
    body = Column(String)

    def __init__(self, title, body, author, id=None):
        self.body = body
        self.author = author
        self.title = title
        self.validate()

    def validate(self):
        if len(self.body) < 10:
            msg = 'blog body too small, needs to be 100 chars'
            d = {
                'title': {'value': self.title},
                'body': {'value': self.body, 'message': msg}
            }
            raise InvalidInput(msg, data=d)

    @classmethod
    def get(cls, id, viewing_user=LOGGED_IN_USER):
        blog = config.session.query(cls).filter_by(id=id).first()
        if not blog:
            raise DataNotFound("Blog does not exist")
        return {'blog': blog, 'viewing_user': viewing_user}

    @classmethod
    def create(cls, title, body, author=LOGGED_IN_USER):
        if not author:
            raise InvalidInput()
        blog = cls(title=title, body=body, author=author)
        config.session.add(blog)
        config.session.commit()
        return blog

    @classmethod
    def edit(cls, id, title, body, author=LOGGED_IN_USER):
        blog = config.session.query(cls).filter_by(id=id).first()
        if not blog.author == author:
            raise DataNotFound("You can't edit other people's blog")

        blog.title = title
        blog.body = body
        blog.validate()

        config.session.add(blog)
        config.session.commit()
        return blog


    @classmethod
    def all(cls, viewing_user=LOGGED_IN_USER):
        blogs = config.session.query(cls).all()
        return {'blogs': blogs, 'viewing_user': viewing_user}

def make_mock_blog(x=1):
    return Blog(
        title="title %s" % x,
        body=("body %s " % x) * 10,
        author=User(username='mock_user', password=""),
    )

def get_blog_mock():
    return {'blog': make_mock_blog(1)}

def blog_index_mock():
    return {
        'blogs': [make_mock_blog(x) for x in xrange(10)],
        'viewing_user': User(username='mock_user', password=""),
    }