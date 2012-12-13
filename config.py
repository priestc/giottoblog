import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import sessionmaker
from giotto.keyvalue import MemcacheKeyValue, RedisKeyValue, LocMemKeyValue, DatabaseKeyValue
from giotto.utils import better_base

Base = better_base()

from sqlite3 import dbapi2 as sqlite
engine = create_engine('sqlite+pysqlite:///file.db', module=sqlite)

session = sessionmaker(bind=engine)()
cache = DatabaseKeyValue(Base, session)
session_store = cache

project_path = os.path.dirname(os.path.abspath(__file__))

from jinja2 import Environment, FileSystemLoader
jinja2_env = Environment(loader=FileSystemLoader(project_path))