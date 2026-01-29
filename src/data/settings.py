import json

class Settings:

    def __init__(self, settings_path):
        try:
            self.json = json.load(open(settings_path))
            self.job_name = self.json["job_name"]
            self.model = self.json["model"]
            self.corrections_path = self.json["corrections_path"]
            self.existing_branch = self.json["existing_branch"]
            self.fails_path = self.json["fails_path"]
            self.response_path = self.json["response_path"]
            self.ignore_files = self.json["ignore_files"]
            self.workspace_path = self.json["workspace_path"]
        except:
            raise Exception("invalid settings")

