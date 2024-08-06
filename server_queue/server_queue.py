from workflows.controller import Workflow
from configuration.config import ADDRESSES

from sqlalchemy import String, ForeignKey, Float, Boolean, select, delete, update
from sqlalchemy.orm import Mapped, mapped_column, Session
from sqlalchemy.ext.hybrid import hybrid_property

from model import Base, queue_engine


class Queue(Base):
    __tablename__ = "Queue"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    _prompt: Mapped[str] = mapped_column("prompt", String)
    _negative_prompt: Mapped[str] = mapped_column("negative_prompt", String)
    _workflow: Mapped[str] = mapped_column("workflow", String)
    _dimensions: Mapped[str] = mapped_column("dimensions", String)
    _user_id: Mapped[str] = mapped_column("user_id", String)
    _upload_image_name: Mapped[str] = mapped_column("upload_image_name", String)
    _server_address: Mapped[str] = mapped_column("server_address", String)

    @classmethod
    def add_new_queue_item(cls, prompt, negative_prompt, workflow, dimensions, user_id, upload_image_name, server_address):
        with Session(queue_engine) as session:
            queue_item = Queue(prompt=prompt, negative_prompt=negative_prompt, workflow=workflow, dimensions=dimensions, user_id=user_id, upload_image_name=upload_image_name, server_address=server_address)
            session.add(queue_item)
            session.commit()


    @classmethod
    def delete_queue_item(cls, r_id):
        with Session(queue_engine) as session:
            row = session.get(Queue, r_id)
            session.delete(row)
            session.commit()
            return row


    @classmethod
    def get_queue(cls):
        with Session(queue_engine) as session:
            return list(session.query(Queue).order_by(Queue.id))


    @classmethod
    def get_server_queue(cls, address):
        with Session(queue_engine) as session:
            return session.scalars(select(Queue).where(Queue.server_address == address))
        

    @classmethod
    def get_queue_length(cls):
        with Session(queue_engine) as session:
            return session.query(Queue).count()


    @classmethod
    def get_queue_item_by_id(cls, id):
        with Session(queue_engine) as session:
            return session.get(Queue, id)
        

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
    

    @hybrid_property
    def upload_image_name(self):
        return self._upload_image_name
    

    @upload_image_name.setter
    def upload_image_name(self, upload_image_name):
        self._upload_image_name = upload_image_name

    
    @hybrid_property
    def server_address(self):
        return self._server_address
    

    @server_address.setter
    def server_address(self, server_address):
        self._server_address = server_address


# DEPRECATED:
# class QueueItem:
#     def __init__(self, prompt: str, workflow: Workflow, dimensions: str, user_id: str, length: int = None, negative_prompt: str = ""):
#         self._prompt = prompt
#         self._workflow = workflow
#         self._dimensions = dimensions
#         self._user_id = user_id
#         self._length = length
#         self._negative_prompt = negative_prompt


#     def negative_prompt(self, negative_prompt: str | None = None) -> str | None:
#         if negative_prompt:
#             self._negative_prompt = negative_prompt
#         else:
#             return self._negative_prompt


#     def length(self, length: str | None = None) -> str | None:
#         if length:
#             self._length = length
#         else:
#             return self._length
    
#     def user_id(self, user_id: str | None = None) -> str | None:
#         if user_id is not None:
#             self._user_id = user_id
#         else:
#             return self._user_id
        
    
#     def prompt(self, prompt: str | None = None) -> str | None:
#         if prompt is not None:
#             self._prompt = prompt
#         else:
#             return self._prompt
        

#     def workflow(self, workflow: Workflow | None = None) -> Workflow | None:
#         if workflow is not None:
#             self._workflow = workflow
#         else:
#             return self._workflow
        

#     def dimensions(self, dimensions: str | None = None) -> str | None:
#         if dimensions is not None:
#             self._dimensions = dimensions
#         else:
#             return self._dimensions


# class ServerQueue:
#     def __init__(self):
#         self._queue = []

    
#     def add_to_queue(self, queue_item: QueueItem):
#         self._queue.append(queue_item)

    
#     def get_length(self):
#         return len(self._queue)
    
    
#     def advance_queue(self) -> QueueItem | None:
#         if len(self._queue) != 0:
#             return self._queue.pop()


# QUEUE = ServerQueue()
Base.metadata.create_all(queue_engine)