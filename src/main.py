import os
from langchain.tools import tool

from agents.contextManager import ContextManager
from agents.manager import AgentManager
from data.settings import Settings
from data.job import Job
from data.replaces import Replaces
from workspace import Workspace
from writer import Writer

settings_path = "settings.json"
settings = Settings(settings_path)
job = Job(settings)
workspace = Workspace(settings, job.source, settings.ignore_files)
workspace.commit("existing changes")
writer = Writer(settings, workspace.path)

def sanitize_path(filename: str) -> str:
    filename = filename.replace(' ', '')
    if filename.startswith('/'): filename = filename[1:]
    return os.path.join(workspace.path, filename)

replaces = Replaces(sanitize_path)

@tool("replace_in_file", description="Replace existing text in the file, given the path of the file (USE THE SAME PATH PROVIDED BY LIST_FILES TOOL), the full and complete text to be replaced and the full and complete new text. DO NOT ABBREVIATE WITH '...'. IF IN TROUBLE USE SHORTER TEXT.")
def replace(filepath:str, old:str, new:str) -> str:
    """Replace text in a file.

    Args:
        filepath (str): The path of the file from the project root "/".
        old (str): The existing text in the file to be replaced.
        new (str): The new code corrected.
    """
    tmp = replaces.replace(filepath, old, new)
    if "Failed" in tmp:
        print(f"[TOOL] NOT REPLACED in {filepath}")
        writer.write_in_fails(f"## NOT REPLACED \n{old} \nIN {filepath}\n\n")
        return f"{tmp} replace in {filepath} be sure 'old' match some text in the actual file content, READ THE ORIGINAL FILE AND MATCH THE SAME EXACT TEXT."
    if "applied" in tmp:
        writer.write_in_corrections(f"# REPLACED \nwrong: {old} \n\ncorrect: {new}\n\n")
        print(f"[TOOL] REPLACED IN {filepath}")
        replaces.add_replace(filepath, old, new)
    else:
        print(f"[TOOL] Not found: {filepath}")
    return tmp

@tool("list_files", description="List all project files.")
def list() -> list:
    """list project files.
    """
    print(f"[TOOL] LISTING FILES")
    print(workspace.files)
    return workspace.files

@tool("write_file", description="Write text in file given its path starting with '/'.")
def write(filepath:str, text:str):
    """Write text in a file.

    Args:
        filepath (str): The path of the file from the root.
        text (str): The text to write.
    """
    file_path = sanitize_path(filepath)
    print(f"[TOOL] WRITING {filepath}")
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(text)
    except Exception as e:
        print(str(e))

@tool("read_file", description="Read file content text.")
def read(filepath:str) -> str:
    """Read text from a file

    Args:
        filepath (str): The path of the file from the root
    """
    file_path = sanitize_path(filepath)
    print(f"[TOOL] READING {filepath}")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(str(e))
        return "File does not exists or path is incomplete"

@tool("end_work", description="End the work, CALL THIS TOOL ONLY IF ALLOWED BY THE USER. After calling this write a message to end the conversation.")
def end_work():
    """End the work, CALL THIS TOOL ONLY IF SPECIFIED BY THE USER.
    """
    print(f"[TOOL] Work terminated.")
    job.ia_wants_terminate = True

write_tools = [write, replace]
read_tools = [list, read]

for i in range(0, job.numero_esecuzioni):
    agents_manager = AgentManager(writer, read_tools, write_tools, end_work)
    agents_manager.chat(job, writer, workspace)
    replaces.clear()
