import json
from data.settings import Settings
from data.prompt import Prompt

class Writer:

    def __init__(self, settings: Settings):
        self.settings = settings
        self.log_settings_in_response()
        with open(self.settings.corrections_path, 'w', encoding='utf-8') as c: # Clear/create file
            pass
        with open(self.settings.fails_path, 'w', encoding='utf-8') as c: # Clear/create file
            pass
        with open(self.settings.response_path, 'w', encoding='utf-8') as c: # Clear/create file
            pass

    def write_in_response(self, text: str):
        with open(self.settings.response_path, 'a', encoding='utf-8') as c:
            c.write(text)
    
    def write_in_corrections(self, text: str):
        with open(self.settings.corrections_path, 'a', encoding='utf-8') as c:
            c.write(text)

    def write_in_fails(self, text: str):
        with open(self.settings.fails_path, 'a', encoding='utf-8') as c:
            c.write(text)

    def log_settings_in_response(self):
        with open(self.settings.response_path, 'w', encoding='utf-8') as f:
            f.write(json.dumps(self.settings.json, indent=4))
    
