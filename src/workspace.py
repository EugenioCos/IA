import os, random, string, shutil
from git import Repo
from git.cmd import Git

from data.settings import Settings

class Workspace:

    def __init__(self, settings: Settings, project_path: str, files: list[str]):
        self.settings = settings
        print(f"Project_path: {project_path}")
        self.project_files: list[str] = []
        for file in files:
            self.project_files.append(os.path.join(project_path, file))
        for file in self.project_files:
            print(f"project_file: {file}")
        self.create_branch_name()
        self.init_workspace(project_path)
        self.create_branch(project_path)
        print(f"Workspace_path: {self.path}")

    def create_branch_name(self):
        if self.settings.existing_branch is None:
            random_id = ''.join(random.choices(string.digits, k=4))
            self.branch_name = f"{self.settings.job_name}_{random_id}"
        else:
            self.branch_name = self.settings.existing_branch

    def create_branch(self, project_path):
        git_path = os.path.join(self.path, ".git")
        if self.settings.existing_branch is None: 
            project_git_path = os.path.join(project_path, ".git")
            shutil.copytree(project_git_path, git_path)
        self.repo = Repo(git_path)
        self.git_cmd = self.repo.git
        if self.settings.existing_branch is None: 
            self.git_cmd.checkout("HEAD", b=self.branch_name)  # Create a new branch.
        
    def init_workspace(self, project_path):
        self.path = os.path.join(self.settings.workspace_path, self.branch_name)
        self.files = [os.path.join(self.path, os.path.relpath(file_path, project_path)) for file_path in self.project_files]
        print(f"Workspace in {self.path}, from {project_path}")
        if self.settings.existing_branch is not None: return
        for i, file in enumerate(self.project_files):
            os.makedirs(os.path.dirname(self.files[i]), exist_ok=True)
            shutil.copyfile(file, self.files[i])

    def commit(self, commit_message: str) -> bool:
        self.repo.index.add(self.files)
        if '.' not in self.git_cmd.diff("--cached", "--name-only"):
            return False
        self.repo.index.commit(commit_message)
        print("Commit done")
        return True