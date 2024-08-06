from workflows.controller import Workflow
from configuration.config import ADDRESSES

from sqlalchemy import String, ForeignKey, Float, Boolean, select, delete
from sqlalchemy.orm import Mapped, mapped_column, Session
from sqlalchemy.ext.hybrid import hybrid_property

from model import Base, queue_engine


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

    
    @classmethod
    def find_available(cls, session):
        print('available for text')
        server = session.scalar(select(Server).where(Server.busy == 0))
        return server
    

    @classmethod
    def find_available_for_video(cls, session):
        print('available for video')
        server = session.scalar(select(Server).where(Server.busy == 0).where(Server.for_video == 1))
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


# class ServerList:
#     def __init__(self, servers: list[Server]):
#         self._servers = servers

    
#     def find_avaiable_server(self) -> Server | None:
#         for server in self._servers:
#             if not server.busy():
#                 return server
        
class Queue:
    __tablename__ = "Queue"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    _prompt: Mapped[str] = mapped_column("prompt", String)
    _negative_prompt: Mapped[str] = mapped_column("negative_prompt", String)
    _workflow: Mapped[str] = mapped_column("workflow", String)
    _dimensions: Mapped[str] = mapped_column("dimensions", String)
    _user_id: Mapped[str] = mapped_column("user_id", String)

    @hybrid_property
    def prompt(self):
        return self._prompt
    

    @prompt.setter
    def prompt(self, prompt):
        self._prompt = prompt

    
    @hybrid_property
    def negative_prompt(self):
        return self._negative_prompt
    

    @negative_prompt.setter
    def negative_prompt(self, prompt):
        self._negative_prompt = prompt


    @hybrid_property
    def workflow(self):
        return self._workflow
    

    @workflow.setter
    def workflow(self, workflow):
        self._workflow = workflow

    
    @hybrid_property
    def dimensions(self):
        return self._dimensions
    

    @dimensions.setter
    def dimensions(self, dimensions):
        self._dimensions = dimensions


    @hybrid_property
    def user_id(self):
        return self._user_id
    

    @user_id.setter
    def user_id(self, user_id):
        self._user_id = user_id
    


class QueueItem:
    def __init__(self, prompt: str, workflow: Workflow, dimensions: str, user_id: str, length: int = None, negative_prompt: str = ""):
        self._prompt = prompt
        self._workflow = workflow
        self._dimensions = dimensions
        self._user_id = user_id
        self._length = length
        self._negative_prompt = negative_prompt


    def negative_prompt(self, negative_prompt: str | None = None) -> str | None:
        if negative_prompt:
            self._negative_prompt = negative_prompt
        else:
            return self._negative_prompt


    def length(self, length: str | None = None) -> str | None:
        if length:
            self._length = length
        else:
            return self._length
    
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

Base.metadata.create_all(queue_engine)
with Session(queue_engine) as session:
    session.query(Server).delete()
    SERVER_LIST = [Server(address=server['address'], eta=-1.0, busy=False, for_video=server['for_video']) for server in ADDRESSES]
    session.add_all(SERVER_LIST)
    session.commit()

