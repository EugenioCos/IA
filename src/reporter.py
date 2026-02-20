import json, os
from data.prompt import Prompt
from langchain.messages import AnyMessage

class Reporter:

    def __init__(self, send_function):
        self.send_function = send_function

    # Tools

    def list_files(self) -> str:
        message = { "command": "list" }
        return self.send_function(message)
    
    def write_in_file(self, file_path, text) -> str:
        message = { "command": "write_in_file", "file_path": file_path, "text": text }
        return self.send_function(message)
    
    def read_file(self, file_path) -> str:
        message = { "command": "read_file", "file_path": file_path }
        return self.send_function(message)

    def replace_in_file(self, file_path, old, new) -> str:
        message = { "command": "replace_in_file", "file_path": file_path, "new": new, "old": old }
        return self.send_function(message)

    def commit(self, title: str) -> str:
        message = { "command": "commit", "title": title }
        return self.send_function(message)
    
    def revert_commit(self) -> str:
        message = { "command": "revert_commit"}
        return self.send_function(message)
    
    # Logs

    def write_in_response(self, content: str | list[tuple[str, str]]):
        message = { "command": "response", "content": content }
        self.send_function(message)

    def log_context(self, prompt_title, messages: list[tuple[str, str]]):
        message = { "command": "context", "prompt_title": prompt_title, "context": messages }
        self.send_function(message)

    def log_settings_in_response(self, settings):
        self.write_in_response(json.dumps(settings.json, indent=4))

    def log_prompt_in_response(self, prompt: Prompt):
        print(str(prompt))
        self.write_in_response(str(prompt))

    
