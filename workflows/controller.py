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
    file_type = "mp4"
    folder = "videos"
    requires_image_upload = False

    def __init__(self):
        self.load_workflow('format_check.json')
        

class WorkflowTextToImage(Workflow):
    file_type = "png"
    folder = "photos"
    requires_image_upload = False
    
    def __init__(self):
        self.load_workflow('t2i_two_passes.json')
        

class WorkflowImageToVideo(Workflow):
    file_type = "mp4"
    folder = "videos"
    requires_image_upload = True
    
    def __init__(self):
        self.load_workflow('image_to_video.json')

WORKFLOW_MAPPING = {
    "t2i": WorkflowTextToImage,
    "t2v": WorkflowTextToVideo,
    "i2v": WorkflowImageToVideo
}