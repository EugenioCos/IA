import os
from langchain.tools import tool

from contextManager import ContextManager
from data.settings import Settings
from data.job import Job
from agentManager import AgentManager
from workspace import Workspace
from writer import Writer

settings_path = "settings.json"
settings = Settings(settings_path)
job = Job(settings)
context_manager = ContextManager(job.root, settings.ignore_files)
workspace = Workspace(settings, job.root, context_manager.files)
workspace.commit("existing changes")
writer = Writer(settings)

def correct_in_file_examples() -> str:
    with open(settings.corrections_path, 'r', encoding='utf-8') as f:
        return f"correzioni esempio (che sono state applicate con succhesso): {f.read()}"

@tool("correct_in_file", description="Correct code in a file given the path of the file starting with '/' by replacing it. read file to get the exact wrong text to be replaced and do not abbreviate with '...'. IF IN TROUBLE USE SHORTER TEXT.")
def correct(filepath:str, old:str, new:str) -> str:
    """Correct code in a file.

    Args:
        filepath (str): The path of the file from the project root "/".
        old (str): The code in the file to be correctd.
        new (str): The new code corrected.
    """
    if ".py" in filepath and "/src/" not in filepath:
        file_path = workspace.path+"/src/"+filepath
    else: file_path = workspace.path+filepath
    try:
        # Read old content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        # Correct old content
        new_content = content.replace(old, new).strip()
        # Check correction
        if new_content == content: 
            print(f"[TOOL] NOT REPLACED in {filepath}")
            writer.write_in_fails(f"## NOT REPLACED \n{old} \nIN {filepath}\n\n")
            return f"'old' is not in the file. {correct_in_file_examples()}" #  Actual file content: {content}"
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
            return "Correction applied, text changed."
        writer.write_in_corrections(f"# REPLACED \nwrong: {old} \n\ncorrect: {new}\n\n")
        print(f"[TOOL] REPLACED IN {filepath}")
    except Exception as e:
        print(f"[TOOL] Error replacing {old} with {new}in {filepath}")
        return "Path incorrect, be sure to use a full path"

@tool("list_files", description="List all project files.")
def list() -> list:
    """list project files.
    """
    print(f"[TOOL] LISTING FILES")
    return context_manager.files

@tool("write_file", description="Write text in file given its path starting with '/'.")
def write(filepath:str, text:str):
    """Write text in a file.

    Args:
        filepath (str): The path of the file from the root.
        text (str): The text to write.
    """
    file_path = workspace.path+filepath
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
    if ".py" in filepath and "/src/" not in filepath:
        file_path = workspace.path+"/src"+filepath
    else: file_path = workspace.path+filepath
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

tools = [list, read, write, correct, end_work]

agentManager = AgentManager(tools)

with open(settings.response_path, 'a', encoding='utf-8') as f:
    while job.get_prompt():
        # Preparazione contesto e prompt
        prompt = job.get_prompt()
        prompt.log_prompt(f)
        context = context_manager.get_context(prompt.context)
        context.append(prompt.get_message()) # I prompt non sono preservati nei contesti successivi
        # Risposta e elaborazione post-risposta
        resp_messages = agentManager.generate_response(context, prompt.think, prompt.tools, f)
        print("Prompt done")
        context_manager.add_messages(resp_messages)
        if prompt.commit:
            edited = workspace.commit("update")
            if prompt.commit is not None and edited != prompt.commit:
                if(prompt.commit): msg ="[SYSTEM] NON HAI MODIFICATO I FILE, RIPROVA UTILIZZANDO I TOOL CHE HAI A DISPOSIZIONE. PROVA A LEGGERE I FILE ORIGINAL E SOTITUIRE PORZIONI DI CODICE PIù BREVI SE NON RIESCI A USARE IL TOOL 'correct'"
                else: msg = "[SYSTEM] HAI MODIFICATO FILE, QUINDI SERVONO ULTERIORI CONTROLLI"
                context_manager.add_message(msg, "system")
                print(msg)
                job.go_back(prompt.post_flow)
                continue
        if(prompt.permit_end):
            if not job.ia_wants_terminate:
                job.go_back(prompt.post_flow)
        job.next()
