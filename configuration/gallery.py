import json
import os

class Gallery:
    def __init__(self):
        with open(os.path.join(os.path.dirname(__file__), 'gallery', 'gallery.json')) as f:
            self.mappings = json.load(f)


gallery = Gallery()
