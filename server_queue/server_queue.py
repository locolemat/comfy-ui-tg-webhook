from workflows.controller import Workflow
from configuration.config import ADDRESSES

from sqlalchemy import String, ForeignKey, Float, Boolean, select, delete
from sqlalchemy.orm import Mapped, mapped_column, Session
from sqlalchemy.ext.hybrid import hybrid_property

from model import Base, engine


class Server(Base):
    __tablename__ = "Servers"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    _address: Mapped[str] = mapped_column("address", String(30))
    _eta_coefficient: Mapped[float] = mapped_column("eta_coefficient", Float)
    _busy: Mapped[bool] = mapped_column("busy", Boolean)

    
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
    def eta_coefficient(self):
        return self._eta_coefficient
    

    @eta_coefficient.setter
    def eta_coefficient(self, eta_coefficient):
        self._eta_coefficient = eta_coefficient

    
    @classmethod
    def find_available(cls, session):
        server = session.scalar(select(Server).where(Server.busy == 0))
        return server


    def __repr__(self):
        return f'Server ID{self.id}: {self.address}, currently busy: {self.busy}. ETA Coefficient: {self.eta_coefficient}'

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


class ServerList:
    def __init__(self, servers: list[Server]):
        self._servers = servers

    
    def find_avaiable_server(self) -> Server | None:
        for server in self._servers:
            if not server.busy():
                return server
        

class QueueItem:
    def __init__(self, prompt: str, workflow: Workflow, dimensions: str, user_id: str, length: int = None):
        self._prompt = prompt
        self._workflow = workflow
        self._dimensions = dimensions
        self._user_id = user_id
        self._length = length


    def length(self, length: str | None = None) -> str | None:
        if length:
            self._length = length
        else:
            return self.length
    
    def user_id(self, user_id: str | None = None) -> str | None:
        if user_id is not None:
            self._user_id = user_id
        else:
            return self._user_id
        
    
    def prompt(self, prompt: str | None = None) -> str | None:
        if prompt is not None:
            self._prompt = prompt
        else:
            return self._prompt
        

    def workflow(self, workflow: Workflow | None = None) -> Workflow | None:
        if workflow is not None:
            self._workflow = workflow
        else:
            return self._workflow
        

    def dimensions(self, dimensions: str | None = None) -> str | None:
        if dimensions is not None:
            self._dimensions = dimensions
        else:
            return self._dimensions


class ServerQueue:
    def __init__(self):
        self._queue = []

    
    def add_to_queue(self, queue_item: QueueItem):
        self._queue.append(queue_item)

    
    def get_length(self):
        return len(self._queue)
    
    
    def advance_queue(self) -> QueueItem | None:
        if len(self._queue) != 0:
            return self._queue.pop()


QUEUE = ServerQueue()

Base.metadata.create_all(engine)
with Session(engine) as session:
    session.query(Server).delete()
    SERVER_LIST = [Server(address=address, eta_coefficient=-1.0, busy=False) for address in ADDRESSES]
    session.add_all(SERVER_LIST)
    session.commit()

