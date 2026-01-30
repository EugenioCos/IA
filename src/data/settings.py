import json

class Settings:

    def __init__(self, settings_path):
        try:
            self.json = json.load(open(settings_path))
            self.job_name = self.json["job_name"]
            self.model = self.json["model"]
            self.existing_branch = self.json["existing_branch"]
            self.response_dir = self.json["response_dir"]
            self.use_git = self.json["use_git"]
            self.ignore_files = self.json["ignore_files"]
            self.workspace_path = self.json["workspace_path"]
        except:
            raise Exception("invalid settings")

