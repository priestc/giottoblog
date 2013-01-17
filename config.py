import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import sessionmaker
from giotto.keyvalue import MemcacheKeyValue, RedisKeyValue, LocMemKeyValue, DatabaseKeyValue
from giotto.utils import better_base

Base = better_base()

#engine = create_engine('mysql+gaerdbms:///giottoblogdb')

from sqlite3 import dbapi2 as sqlite
engine = create_engine('sqlite+pysqlite:///file.db', module=sqlite)

session = sessionmaker(bind=engine)()
cache = LocMemKeyValue()
auth_session = cache
auth_session_expire = 36000

project_path = os.path.dirname(os.path.abspath(__file__))

from jinja2 import Environment, FileSystemLoader
jinja2_env = Environment(loader=FileSystemLoader(project_path))

debug = False
error_template = 'html/error.html'