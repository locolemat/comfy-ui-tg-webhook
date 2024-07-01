from sqlalchemy import create_engine
from sqlalchemy import String, ForeignKey

from sqlalchemy.orm import DeclarativeBase, Session

engine = create_engine(url="sqlite:///main.db", echo=True)

class Base(DeclarativeBase):
    pass


def create_session():
    return Session(engine)