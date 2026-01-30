import os, random, string, shutil
from git import Repo

from data.settings import Settings

class Workspace:

    files: list[str] = [] # Relative path for each file
    project_files: list[str] = [] # Absolute path for each project file
    workspace_files: list[str] = [] # Absolute path for each project file

    def __init__(self, settings: Settings, project_path: str, ignore_files: list[str]):
        self.settings = settings
        print(f"Project_path: {project_path}")
        self.create_branch_name()
        self.path = self.settings.workspace_path + self.branch_name
        if settings.existing_branch is not None:
            project_path = self.path
        self.scan_files(project_path, ignore_files)
        for file in self.files:
            self.project_files.append(os.path.join(project_path, file))
            self.workspace_files.append(os.path.join(self.path, file))
            print(f"selected_file: {file}")
        self.init_workspace()
        self.create_branch(project_path)
        print(f"Workspace in {self.path}")

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
        
    def init_workspace(self):
        if self.settings.existing_branch is not None: return
        for i, file in enumerate(self.project_files):
            os.makedirs(os.path.dirname(self.workspace_files[i]), exist_ok=True)
            shutil.copyfile(file, self.workspace_files[i])

    def commit(self, commit_message: str) -> bool:
        self.repo.index.add(self.workspace_files)
        if '.' not in self.git_cmd.diff("--cached", "--name-only"):
            return False
        self.repo.index.commit(commit_message)
        print("Commit done")
        return True
    
    def scan_files(self, root_path: str, ignore_files: list[str]) -> None:
        if not os.path.isabs(root_path):
            raise Exception("Path is not absolute")
        if not os.path.isdir(root_path):
            raise Exception("Directory not found")

        for root, dirs, files in os.walk(root_path):
            dirs[:] = [d for d in dirs if d not in ignore_files]
            for filename in files:
                if filename in ignore_files:
                    continue

                # Process the file (e.g., read, write, etc.)
                file_path = os.path.join(root, filename)
                filtered = file_path.replace(root_path+"/", "")
                self.files.append(filtered)

                