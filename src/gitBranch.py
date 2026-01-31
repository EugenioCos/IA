import os, shutil
from git import Repo

class GitBranch:

    def __init__(self, project_path, existing=bool):
        self.existing = existing
        self.read_ignore_list(project_path)

    def init(self, project_path, workspace_path, branch_name):
        git_path = os.path.join(workspace_path, ".git")
        if not self.existing:
            self.create_git(project_path, git_path)
        self.repo = Repo(git_path)
        self.git_cmd = self.repo.git
        if not self.existing:
            self.git_cmd.checkout("HEAD", b=branch_name) # Create a new branch.

    def create_git(self, project_path, git_path):
        project_git_path = os.path.join(project_path, ".git")
        shutil.copytree(project_git_path, git_path)

    def read_ignore_list(self, project_path):
        gitignore_path = os.path.join(project_path, ".gitignore")
        try:
            with open(gitignore_path, 'r', encoding="utf-8") as f:
                file_list = f.readlines()
                self.ignore_files = [file.strip() for file in file_list if file is not None] + [".git"]
        except Exception as e:
            print("No .gitignore file found")
            self.ignore_files = [".git"]

    def get_ignore_files(self):
        return self.ignore_files

    def commit(self, commit_message: str, files: list[str]) -> bool:
        self.repo.index.add(files)
        if '.' not in self.git_cmd.diff("--cached", "--name-only"):
            return False
        self.repo.index.commit(commit_message)
        print("Commit done")
        return True