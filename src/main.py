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

@tool
def replace_in_file(filepath:str, old:str, new:str) -> str:
    """Replace existing text in the file, given the path of the file CONTRAINTS: [ USE THE SAME PATH PROVIDED BY LIST_FILES TOOL, AS 'old' MATCH THE SAME EXACT TEXT WITH SAME INDENT AND ALL EXACT CHARACTERS WITHOUT ABBREVIATIONS, DO NOT ABBREVIATE ]

    Args:
        filepath (str):  The path of the file as provided by 'list_files' tool.
        old (str): The existing text in the file to be replaced.
        new (str): The new code corrected.
    """
    tmp = replaces.replace(filepath, old, new)
    if "Failed" in tmp:
        print(f"[TOOL] NOT REPLACED in {filepath}")
        writer.write_in_fails(f"## NOT REPLACED \n{old} \nIN {filepath}\n\n")
        return f"{tmp} replace in {filepath} be sure 'old' match some text in the actual file content DO NOT ADD WHITESPACES AT THE END OF THE LINE; PRESERVE SAME EXACT WHITESPACES AS THEY ARE. READ THE ORIGINAL FILE AND MATCH THE SAME EXACT CHARACTERS ORDER."
    if "applied" in tmp:
        writer.write_in_corrections(f"# REPLACED \nwrong: {old} \n\ncorrect: {new}\n\n")
        print(f"[TOOL] REPLACED IN {filepath}")
        replaces.add_replace(filepath, old, new)
    else:
        print(f"[TOOL] Not found: {filepath}")
    return tmp

@tool
def list_files() -> list[str]:
    """list project files.
    """
    print(f"[TOOL] LISTING FILES")
    return workspace.files

@tool
def write_in_file(filepath:str, text:str):
    """Write text in a file.

    Args:
        filepath (str): The path of the file as provided by 'list_files' tool.
        text (str): The text to write.
    """
    file_path = sanitize_path(filepath)
    print(f"[TOOL] WRITING {filepath}")
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(text)
    except Exception as e:
        print(str(e))
    return None

@tool
def read_file(filepath:str) -> str:
    """Read text from a file

    Args:
        filepath (str): The path of the file as provided by 'list_files' tool.
    """
    file_path = sanitize_path(filepath)
    print(f"[TOOL] READING {filepath}")
    text = ""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
    except Exception as e:
        print(str(e))
        return "File does not exists or path is incomplete"
    return text

@tool("reject", description="USE THIS TOOL TO TELL THE USER THAT YOU REJECT")
def reject() -> str:
    """USE THIS TOOL TO TELL THE USER YOUR DECISION TO REJECT.
    """
    job.add_vote(False)
    return "STOP_45F"

@tool("approve", description="USE THIS TOOL TO TELL THE USER THAT YOU APPROVE")
def approve() -> str:
    """USE THIS TOOL TO TELL THE USER YOUR DECISION TO APPROVE.
    """
    job.add_vote(True)
    return "STOP_45F"

tools_dict = {
    "decide_tools": [approve, reject],
    "write_tools": [replace_in_file, write_in_file],
    "read_tools": [list_files, read_file]
}

for i in range(0, job.numero_esecuzioni):
    agents_manager = AgentManager(writer, job, tools_dict)
    agents_manager.chat(writer, workspace)
    job.reset()
    #replaces.clear()
