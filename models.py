from giotto.exceptions import InvalidInput, DataNotFound
from giotto.contrib.auth.models import User

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

    def __init__(self, title, body):
        if len(body) < 100:
            d = {
                'title': {'value': title},
                'body': {'value': body, 'message': 'blog body too small, needs to be 100 chars'}
            }
            raise InvalidInput(data=d)
        self.body = body
        self.title = title

    @classmethod
    def get(cls, id):
        ret = config.session.query(cls).filter_by(id=id).first()
        if not ret:
            raise DataNotFound
        return ret

    @classmethod
    def create(cls, title, body):
        blog = cls(title=title, body=body)
        config.session.add(blog)
        config.session.commit()
        return blog

    @classmethod
    def all(cls):
        return config.session.query(cls).all()