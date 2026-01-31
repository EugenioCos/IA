import json, os
from data.settings import Settings
from data.prompt import Prompt
from langchain.messages import AnyMessage

class Writer:

    context_index = 0

    def __init__(self, settings: Settings, branch_path:str):
        self.response_dir = os.path.join(branch_path, settings.response_dir)
        self.corrections_path = os.path.join(self.response_dir, "corrections.md")
        self.context_path = os.path.join(self.response_dir, "contexts/context_")
        self.fails_path = os.path.join(self.response_dir, "fails.md")
        self.response_path = os.path.join(self.response_dir, "response.md")
        if settings.existing_branch is None:
            self.create_files()
            path = os.path.join(branch_path, self.context_path)
            os.makedirs(os.path.dirname(path), exist_ok=True)
        print(self.response_path)
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

    def log_context(self, messages: list[tuple[str, str]]):
        path = self.context_path+str(self.context_index)+".md"
        self.context_index = self.context_index + 1
        print(f"Contesto salvato in {path}")
        mode = 'w' if os.path.exists(path) else 'x'
        with open(path, mode, encoding='utf-8') as f:
            for message in messages:
                f.write(f"[{message[0]}] {message[1]}\n\n")
            f.flush()

    def log_settings_in_response(self, settings):
        self.write_in_response(json.dumps(settings.json, indent=4))

    def log_prompt_in_response(self, prompt: Prompt):
        print(str(prompt))
        self.write_in_response(str(prompt))

    def write_messages_in_response(self, messages: list[tuple[str, str]], think):
        for message in messages:
            self.write_in_response(f"[{message[0]}] {message[1]}")

    def create_files(self):
        os.makedirs(self.response_dir)
        with open(self.corrections_path, 'w', encoding='utf-8') as c: # Clear/create file
            pass
        with open(self.fails_path, 'w', encoding='utf-8') as c: # Clear/create file
            pass
        with open(self.response_path, 'w', encoding='utf-8') as c: # Clear/create file
            pass

    
