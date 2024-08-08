from configuration.config import ADDRESSES

from sqlalchemy import String, Float, Boolean, select
from sqlalchemy.orm import Mapped, mapped_column, Session
from sqlalchemy.ext.hybrid import hybrid_property

from model import Base, engine, create_session_queue, create_session
from .server_queue import Queue
from propagation import queue_work

class Server(Base):
    __tablename__ = "Servers"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    _address: Mapped[str] = mapped_column("address", String(30))
    _eta: Mapped[float] = mapped_column("eta", Float)
    _busy: Mapped[bool] = mapped_column("busy", Boolean)
    _for_video: Mapped[bool] = mapped_column("for_video", Boolean)


    @hybrid_property
    def address(self):
        return self._address
    

    @address.setter
    def address(self, address):
        self._address = address
        
    
    @hybrid_property
    def busy(self):
        return self._busy
    

    @busy.setter
    def busy(self, busy):
        self._busy = busy


    @hybrid_property
    def for_video(self):
        return self._for_video
    

    @for_video.setter
    def for_video(self, for_video):
        self._for_video = for_video


    @hybrid_property
    def eta(self):
        return self._eta
    

    @eta.setter
    def eta(self, eta):
        self._eta = eta
        with create_session() as session:
            this_server = Server.find_server_by_address(session=session, address=self.address)
            this_server.eta = eta
            session.commit()

    
    @classmethod
    def find_available_for_text(cls, session):
        print('available for text')
        server = session.scalars(select(Server).where(Server.for_video == 0))
        return server
    

    @classmethod
    def find_available_for_video(cls, session):
        print('available for video')
        server = session.scalars(select(Server).where(Server.for_video == 1))
        return server
    

    @classmethod
    def get_all_servers(cls):
        with Session(engine) as session:
            return list(session.query(Server))
        

    @classmethod
    def find_server_by_address(cls, session, address):
        server = session.scalar(select(Server).where(Server.address == address))
        return server


    def __repr__(self):
        return f'Server ID{self.id}: {self.address}, currently busy: {self.busy}. ETA Coefficient: {self.eta_coefficient}'


    async def server_polling(self): 
        with create_session_queue() as session:
            queue = Queue.get_server_queue(self.address, session)
            for queue_item in queue:
                queue_item.processed = True
                print("UPDATED PROCESSED STATUS")
                session.commit()
                print(f"started polling on server {self.address}")
                await queue_work(queue_item=queue_item, workflow=queue_item.workflow, server=self)


    # def __init__(self, address: str, busy: bool = False):
    #     self._address = address
    #     self._busy = busy

    # def address(self, address: str | None = None) -> str | None:
    #     if address:
    #         self.address = address



    # def address(self, address: str | None = None) -> str | None:
    #     if address is not None:
    #         self._address = address
    #     else:
    #         return self._address
        

    # def busy(self, busy: bool | None = None) -> bool | None:
    #     if busy is not None:
    #         self._busy = busy
    #     else:
    #         return self._busy


# class ServerList:
#     def __init__(self, servers: list[Server]):
#         self._servers = servers

    
#     def find_avaiable_server(self) -> Server | None:
#         for server in self._servers:
#             if not server.busy():
#                 return server


Base.metadata.create_all(engine)