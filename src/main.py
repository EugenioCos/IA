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
context_manager = ContextManager(job, settings.ignore_files)
workspace = Workspace(settings, job.root, context_manager.files)
workspace.commit("existing changes")
writer = Writer(settings, workspace.path)

def sanitize_path(filename: str) -> str:
    filename = filename.replace(' ', '')
    if ".py" in filename and "/src/" not in filename:
        file_path = workspace.path + "/src/" + filename
    else:
        file_path = workspace.path + filename
    return file_path


def correct_in_file_examples() -> str:
    with open(settings.corrections_path, 'r', encoding='utf-8') as f:
        return f"correzioni esempio (che sono state applicate con succhesso): {f.read()}"

@tool("replace_in_file", description="Replace existing text in the file, given the path of the file starting with '/', the full and complete text to be replaced and the full and complete new text. DO NOT ABBREVIATE WITH '...'. IF IN TROUBLE USE SHORTER TEXT.")
def replace(filepath:str, old:str, new:str) -> str:
    """Replace text in a file.

    Args:
        filepath (str): The path of the file from the project root "/".
        old (str): The existing text in the file to be replaced.
        new (str): The new code corrected.
    """
    file_path = sanitize_path(filepath)
    try:
        # Read old content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        # Correct old content
        new_content = content.replace(old.strip(), new.strip()).strip()
        # Check correction
        if new_content == content: 
            print(f"[TOOL] NOT REPLACED in {filepath}")
            writer.write_in_fails(f"## NOT REPLACED \n{old} \nIN {filepath}\n\n")
            return f"Failed, be sure 'old' match some text in the actual file content: ### START ### {content} ### END ###"
        writer.write_in_corrections(f"# REPLACED \nwrong: {old} \n\ncorrect: {new}\n\n")
        print(f"[TOOL] REPLACED IN {filepath}")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
            return "Correction applied, text changed."
    except Exception as e:
        print(f"[TOOL] Error replacing {old} with {new}in {filepath}")
        return "Path incorrect, be sure to use a full path"

@tool("list_files", description="List all project files.")
def list() -> list:
    """list project files.
    """
    print(f"[TOOL] LISTING FILES")
    print(context_manager.files)
    return context_manager.files

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
    print(f"[TOOL] READING {file_path}")
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

tools = [list, read, write, replace]

agentManager = AgentManager(tools, end_work, writer)

while job.get_prompt():
    # Preparazione contesto e prompt
    prompt = job.get_prompt()
    writer.log_prompt_in_response(prompt)
    context_manager.add_message("human", prompt.text)
    context = context_manager.get_context(None) #prompt.context)
    # Risposta
    resp_messages = agentManager.generate_response(context, prompt)
    writer.write_messages_in_response(resp_messages, prompt.think)
    context_manager.add_response_messages(resp_messages)
    print("Prompt done")
    # Controllo modifiche effettuate
    if prompt.commit is not None and workspace.commit("update") != prompt.commit:
        if(prompt.commit): message_text = "NON HAI MODIFICATO I FILE, RIPROVA UTILIZZANDO I TOOL CHE HAI A DISPOSIZIONE. PROVA A LEGGERE I FILE ORIGINAL E SOTITUIRE PORZIONI DI CODICE PIù BREVI SE NON RIESCI A USARE IL TOOL 'correct'"
        else: message_text = "HAI MODIFICATO FILE, QUINDI SERVONO ULTERIORI CONTROLLI"
        print(f"[SYSTEM] {message_text}")
        context_manager.add_message("system", message_text)
        job.go_back(prompt.post_flow)
        context_manager.delete_last_steps(prompt.delete_last_steps)
        continue
    # Controllo fine flusso
    if(prompt.permit_end):
        if not job.ia_wants_terminate:
            job.go_back(prompt.post_flow)
        else: break
    else:
        job.ia_wants_terminate = False
    job.next()