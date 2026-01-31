import os, random, string, shutil

from data.settings import Settings
from gitBranch import GitBranch

class Workspace:

    full_files: list[str] = [] # Relative path of all workspace files
    files: list[str] = [] # Relative path of all files selected for IA
    project_files: list[str] = [] # Absolute path for each project file
    workspace_files: list[str] = [] # Absolute path for each workspace file

    def __init__(self, settings: Settings, project_path: str, ignore_files: list[str]):
        self.settings = settings
        print(f"Project_path: {project_path}")
        if settings.existing_branch is None:
            self.init_workspace(project_path, ignore_files)
        else:
            self.init_existing(project_path, ignore_files)
        if settings.use_git:
            self.branch.init(project_path, self.path, self.branch_name)
        for file in self.files:
            print(f"Selected file: {file}")
        print(f"Workspace in {self.path}")

    def init_workspace(self, project_path, ignore_files):
        random_id = ''.join(random.choices(string.digits, k=4))
        self.branch_name = f"{self.settings.job_name}_{random_id}"
        self.path = self.settings.workspace_path + self.branch_name
        self.init_branch(project_path, False)
        self.scan_files(project_path, ignore_files)
        for file in self.full_files:
            workspace_file_path = os.path.join(self.path, file)
            self.workspace_files.append(workspace_file_path)
            os.makedirs(os.path.dirname(workspace_file_path), exist_ok=True)
            shutil.copyfile(os.path.join(project_path, file), workspace_file_path)
        
    def init_existing(self, project_path, ignore_files):
        self.branch_name = self.settings.existing_branch
        self.path = os.path.join(self.settings.workspace_path, self.branch_name)
        self.init_branch(project_path, True)
        self.scan_files(self.path, ignore_files)
        for file in self.files:
            workspace_file_path = os.path.join(self.path, file)
            self.workspace_files.append(workspace_file_path)

    def init_branch(self, project_path, create):
        if self.settings.use_git: self.branch = GitBranch(project_path, create)
        else: self.branch = None

    def commit(self, commit_message: str) -> bool:
        if not self.settings.use_git:
            print("Invalid git instruction with no git allowed, check settings.json and job definition.")
            exit()
        return self.branch.commit(commit_message, self.workspace_files)
    
    def scan_files(self, root_path: str, ignore_files: list[str]) -> None:
        if not os.path.isabs(root_path):
            raise Exception(f"Path is not absolute {root_path}")
        if not os.path.isdir(root_path):
            print(f"[ERROR] Directory not found {root_path}")
            exit()
        ignore_list = self.branch.get_ignore_files()
        # Scan full files list except in .gitignore
        for root, dirs, files in os.walk(root_path):
            dirs[:] = [d for d in dirs if d not in ignore_list]
            for filename in files:
                if filename in ignore_list:
                    continue
                # Process the file (e.g., read, write, etc.)
                file_path = os.path.join(root, filename)
                filtered = file_path.replace(root_path+"/", "")
                self.full_files.append(filtered)
        # Scan files list to be considered by ai
        self.files = self.full_files
        for file_path in self.files:
            if os.path.dirname(file_path) in ignore_files:
                self.files.remove(file_path)
                break
            if os.path.split(file_path)[1] in ignore_files:
                self.files.remove(file_path)
                break
                