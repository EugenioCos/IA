import json, os
from data.settings import Settings
from data.prompt import Prompt
from langchain.messages import AnyMessage

class Writer:

    def __init__(self, settings: Settings, branch_path:str):
        settings = settings
        self.response_dir = os.path.join(branch_path, settings.response_dir)
        self.corrections_path = os.path.join(self.response_dir, "corrections.md")
        self.fails_path = os.path.join(self.response_dir, "fails.md")
        self.response_path = os.path.join(self.response_dir, "response.md")
        print(self.response_path)
        if not settings.existing_branch: self.create_files()
        self.log_settings_in_response(settings)

    def write_in_response(self, text: str):
        with open(self.response_path, 'a', encoding='utf-8') as c:
            c.write("\n\n"+text)
            c.flush()
    
    def write_in_corrections(self, text: str):
        with open(self.corrections_path, 'a', encoding='utf-8') as c:
            c.write("\n\n"+text)
            c.flush()

    def write_in_fails(self, text: str):
        with open(self.fails_path, 'a', encoding='utf-8') as c:
            c.write("\n\n"+text)
            c.flush()

    def log_settings_in_response(self, settings):
        self.write_in_response(json.dumps(settings.json, indent=4))

    def log_prompt_in_response(self, prompt: Prompt):
        print(str(prompt))
        self.write_in_response(str(prompt))

    def write_messages_in_response(self, messages: list[tuple[str, str]], think):
        for message in messages:
            message_text = message[1]
            if not think and "<think>" in message_text:
                no_think_text = message_text.split("<think>")[0] + message_text.split("</think>")[1]
                self.write_in_response(no_think_text)
            else: self.write_in_response(f"[{message[0]}] {message[1]}")

    def create_files(self):
        os.makedirs(self.response_dir)
        with open(self.corrections_path, 'w', encoding='utf-8') as c: # Clear/create file
            pass
        with open(self.fails_path, 'w', encoding='utf-8') as c: # Clear/create file
            pass
        with open(self.response_path, 'w', encoding='utf-8') as c: # Clear/create file
            pass

    
