import jsone
import json
import os

LANGUAGE_FILES_FOLDER = os.path.join(os.path.dirname(__file__), "lang")


class LanguageModel:
    lang_code: str

    def __init__(self, lang_code: str):
        self.lang_code = lang_code

        self.mappings = {}

        with open(os.path.join(LANGUAGE_FILES_FOLDER, f'{lang_code.lower()}.json')) as f:
            self.mappings = json.load(f)
        
        for key in self.mappings:
            setattr(self, key, self.mappings[key])
    
    @classmethod
    def with_context(cls, template: str, context: dict) -> str:
        return jsone.render(template, context)


language = LanguageModel('RU')