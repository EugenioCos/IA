from langchain.tools import tool

from agents.contextManager import ContextManager
from agents.manager import AgentManager
from data.job import Job
from data.replaces import Replaces
from reporter import Reporter

from server import Server

server = Server()
model, agents_dict, job_dict = server.accept_work()
job = Job(job_dict)
reporter = Reporter(server.send_function)
reporter.commit("existing changes")
replaces = Replaces()

@tool
def replace_in_file(file_path:str, old:str, new:str) -> str:
    """Replace existing text in the file, given the path of the file CONTRAINTS: [ USE THE SAME PATH PROVIDED BY LIST_FILES TOOL, AS 'old' MATCH THE SAME EXACT TEXT WITH SAME INDENT AND ALL EXACT CHARACTERS WITHOUT ABBREVIATIONS, DO NOT ABBREVIATE ]

    Args:
        file_path (str):  The path of the file as provided by list.
        old (str): The existing text in the file to be replaced.
        new (str): The new code corrected.
    """
    result = reporter.replace_in_file(file_path, old, new)
    if "Failed" in result:
        return f"Failed replace in {file_path} be sure 'old' match some text in the actual file content SPLIT IN SHORTER REPLACES; PRESERVE SAME EXACT WHITESPACES AS THEY ARE. READ THE ORIGINAL FILE AND MATCH THE SAME EXACT CHARACTERS ORDER."
    elif "applied" in result:
        replaces.add_replace(file_path, old, new)
    return result

@tool
def list_files() -> list[str]:
    """list project files."""
    print(f"[TOOL] LISTING FILES")
    return reporter.list_files()

@tool
def write_in_file(file_path: str, text: str):
    """Write text in a file.

    Args:
        file_path (str): The path of the file as provided in the list.
        text (str): The text to write.
    """
    return reporter.write_in_file(file_path, text)

@tool
def read_file(file_path: str) -> str:
    """Read text from a file

    Args:
        file_path (str): The path of the file as provided in the list.
    """
    return reporter.read_file(file_path)

@tool("reject", description="USE THIS TOOL TO TELL THE USER THAT YOU REJECT")
def reject() -> str:
    """USE THIS TOOL TO TELL THE USER YOUR DECISION TO REJECT."""
    job.add_vote(False)
    return "DECISION RECEIVED" # "STOP_45F" # YOU WILL RECEIVE INSTRUCTIONS IN THE NEXT USER MESSAGE

@tool("approve", description="USE THIS TOOL TO TELL THE USER THAT YOU APPROVE")
def approve():
    """USE THIS TOOL TO TELL THE USER YOUR DECISION TO APPROVE."""
    job.add_vote(True)
    return "DECISION RECEIVED" # "STOP_45F"

tools_dict = {
    "decide_tools": [approve, reject],
    "write_tools": [replace_in_file, write_in_file],
    "read_tools": [list_files, read_file],
}

for i in range(0, job.numero_esecuzioni):
    agents_manager = AgentManager(reporter, job, agents_dict, tools_dict)
    agents_manager.chat()
    job.reset()
    # replaces.clear()
