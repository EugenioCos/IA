from langchain.agents import create_agent

from data.prompt import Prompt

class AgentWrapper:

    ia_replace_instruct = " Per correggere i file usi il tool 'replace_in_file'. Se hai problemi leggi il file che vuoi correggere e assicurati di sostituire codice effettivamente presente."
    
    def __init__(self, agent_dict: dict, read_tools, write_tools):
        self.name: str = agent_dict["name"]
        self.system_prompt: str = agent_dict["system_prompt"]
        self.can_read: bool = agent_dict.get("can_read")
        self.can_write: bool = agent_dict.get("can_write")
        self.can_commit: bool = agent_dict.get("can_commit")
        self.tools = []
        if self.can_read: self.tools.extend(read_tools)
        if self.can_write: 
            self.tools.extend(write_tools)
            self.system_prompt = self.system_prompt + self.ia_replace_instruct

    def get_agent(self, prompt: Prompt, llm, extra_tools):
        # llm.reasoning = prompt.think # Not Working
        tools = self.tools + extra_tools
        return create_agent(
            llm,
            tools=(None if len(tools) == 0 else tools),
            system_prompt=self.system_prompt
        )
    
    def __str__(self):
        text = \
        f"######################## AGENT ######################## \
        \n# name: {self.name} \
        \n# self: {self.system_prompt}"
        if self.can_read is not None: text = text + f"\n# con_read: {str(self.can_read)}"
        if self.can_write is not None: text = text + f"\n# can_write: {str(self.can_write)}"
        #if self.can_commit is not None: text = text + f"\n# can_commit: {str(self.can_commit)} "
        text = text + "n########################################################"
        return text