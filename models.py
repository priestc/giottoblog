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
        if len(self.body) < 100:
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
            raise DataNotFound
        return locals()

    @classmethod
    def create(cls, title, body, author=LOGGED_IN_USER):
        blog = cls(title=title, body=body, author=author)
        config.session.add(blog)
        config.session.commit()
        return locals()

    @classmethod
    def edit(cls, id, title, body, author=LOGGED_IN_USER):
        blog = config.session.query(cls).filter_by(id=id).first()
        if not blog.author == author:
            raise DataNotFound

        blog.title = title
        blog.body = body
        blog.validate()

        config.session.add(blog)
        config.session.commit()
        return blog


    @classmethod
    def all(cls, viewing_user=LOGGED_IN_USER):
        blogs = config.session.query(cls).all()
        return locals()