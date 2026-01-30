import json

class Settings:

    def __init__(self, settings_path):
        try:
            with open(settings_path, 'r') as f:
                self.json = json.load(f)
            self.job_name = self.json["job_name"]
            self.model = self.json["model"]
            self.branch = self.json["branch"]
            self.response_path = self.json["response_path"]
            self.ignore_files = self.json["ignore_files"]
            self.workspace_path = self.json["workspace_path"]
        except FileNotFoundError:
            raise Exception("Settings file not found: {0}".format(settings_path))
        except json.JSONDecodeError:
            raise Exception("Invalid JSON in settings file: {0}".format(settings_path))