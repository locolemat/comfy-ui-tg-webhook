from sqlalchemy import create_engine, Session
from sqlalchemy import String, ForeignKey

from sqlalchemy.orm import DeclarativeBase

engine = create_engine(url="sqlite:///main.db", echo=True)

class Base(DeclarativeBase):
    pass


def create_session():
    return Session(engine)