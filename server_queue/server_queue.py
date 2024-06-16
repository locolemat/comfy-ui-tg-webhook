from workflows.controller import Workflow
from configuration.config import ADDRESSES

class Server:
    def __init__(self, address: str, busy: bool = False):
        self._address = address
        self._busy = busy


    def address(self, address: str | None = None) -> str | None:
        if address is not None:
            self._address = address
        else:
            return self._address
        

    def busy(self, busy: bool | None = None) -> bool | None:
        if busy is not None:
            self._busy = busy
        else:
            return self._busy

class ServerList:
    def __init__(self, servers: list[Server]):
        self._servers = servers

    
    def find_avaiable_server(self) -> Server | None:
        for server in self._servers:
            if not server.busy():
                return server
        

class QueueItem:
    def __init__(self, prompt: str, workflow: Workflow, dimensions: str):
        self._prompt = prompt
        self._workflow = workflow
        self._dimensions = dimensions

    
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
SERVER_LIST = ServerList(servers=[Server(address=address) for address in ADDRESSES])