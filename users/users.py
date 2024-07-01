from model import Base, engine

from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column, Session
from sqlalchemy.ext.hybrid import hybrid_property

class User(Base):
    __tablename__ = 'Users'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    _userid: Mapped[str] = mapped_column("userid", String)
    _username: Mapped[str] = mapped_column("username", String)
    _balance: Mapped[int] = mapped_column("balance", Integer)

    @hybrid_property
    def userid(self):
        return self._userid
    

    @userid.setter
    def userid(self, userid):
        self._userid = userid


    @hybrid_property
    def username(self):
        return self._username
    

    @username.setter
    def username(self, username):
        self._username = username


    @hybrid_property
    def balance(self):
        return self._balance
    

    @balance.setter
    def balance(self, balance):
        self._balance = balance

Base.metadata.create_all(engine)

