import os
import json
import jsone

WORKFLOWS_FOLDER = os.path.join(os.path.dirname(__file__), "workflows")

class Workflow():
    def __init__(self):
        self.file = None

    def get_workflow(self, **kwargs) -> dict:
        return jsone.render(self.file, kwargs)
    
    def load_workflow(self, name):
        with open(os.path.join(WORKFLOWS_FOLDER, name)) as f:
            self.file = json.load(f)
    
class WorkflowTextToVideo(Workflow):
    def __init__(self):
        self.load_workflow('text_to_video.json')

class WorkflowTextToImage(Workflow):
    def __init__(self):
        self.load_workflow('text_to_image.json')

class WorkflowImageToVideo(Workflow):
    def __init__(self):
        self.load_workflow('image_to_video.json')

    
