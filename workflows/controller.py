import os
import json
import jsone

WORKFLOWS_FOLDER = os.path.join(os.path.dirname(__file__), "workflows")

class Workflow():
    def __init__(self):
        self.file = None

    def get_workflow(self, **kwargs) -> dict:
        return jsone.render(self.file, kwargs)
    
class WorkflowTextToVideo(Workflow):
    def __init__(self):
        with open(os.path.join(WORKFLOWS_FOLDER, 'text_to_video.json')) as f:
            self.file = json.load(f)

    
