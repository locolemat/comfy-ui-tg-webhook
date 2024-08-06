from sqlalchemy import create_engine
from sqlalchemy import String, ForeignKey

from sqlalchemy.orm import DeclarativeBase, Session

engine = create_engine(url="sqlite:///main.db", echo=True, isolation_level="READ UNCOMMITTED")
queue_engine = create_engine(url="sqlite:///queue.db", echo=True, isolation_level="READ UNCOMMITTED")

class Base(DeclarativeBase):
    pass


def create_session():
    return Session(engine)


def create_session_queue():
    return Session(queue_engine)