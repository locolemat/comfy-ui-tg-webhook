from model import Base, engine

from sqlalchemy import String, Integer, select
from sqlalchemy.orm import Mapped, mapped_column, Session
from sqlalchemy.ext.hybrid import hybrid_property

class User(Base):
    __tablename__ = 'Users'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    _tgid: Mapped[str] = mapped_column("tgid", String)
    _username: Mapped[str] = mapped_column("username", String)
    _balance: Mapped[int] = mapped_column("balance", Integer)
    _preferred_model: Mapped[str] = mapped_column("preferred_model", String)



    @classmethod
    def check_if_user_exists(cls, tgid: str):
        with Session(engine) as session:
            return session.scalar(select(User).where(User.tgid == tgid))


    @hybrid_property
    def preferred_model(self):
        return self._preferred_model
    

    @preferred_model.setter
    def preferred_model(self, preferred_model):
        self._preferred_model = preferred_model


    @hybrid_property
    def tgid(self):
        return self._tgid
    

    @tgid.setter
    def tgid(self, tgid):
        self._tgid = tgid


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

