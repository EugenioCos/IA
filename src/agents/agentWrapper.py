from langchain.agents import create_agent
from langchain_ollama import ChatOllama

class AgentWrapper:

    ia_tool_instruction = "USA SEMPRE I TOOL A DISPOSIZIONE; DEVI LEGGERE I FILE E FORNIRE RISPOSTE SEMPRE BASATE SUL CONTENUTO REALE DEI FILE; LEGGILI OGNI VOLTA CHE HAI DUBBI; CURIOSITà O TI MANCANO INFORMAZIONI; NON CHIEDERE NULLA MA OTTIENILO UTILIZZANDO I TOOL."
    ia_decide_instruct = "YOU MUST USE 'approve' OR 'reject' TOOLS. USE TOOLS IF YOU NEED MORE INFORMATIONS"
    ia_read_instruct = "PER LEGGERE I FILE USA IL TOOL 'read_file'. IGNORE FILE NOT LISTED BY 'list_files' TOOL"
    ia_replace_instruct = "PER CORREGGERE USE IL TOOL 'replace_in_file' (se hai problemi ecco 2 consigli: 1 - leggi il file che vuoi correggere e assicurati di sostituire codice effettivamente presente. 2 - calcola le sostituzioni efficenti e mirate). "

    def __init__(self, agent_dict: dict, tools_dict, model):
        llm = ChatOllama(
            #model="kimi-k2.5:cloud",
            #model="gpt-oss:120b-cloud",
            model=model,
            reasoning=True,
            temperature=0.1,
            repeat_penalty=1.5,
            #num_ctx=4096,
            #num_predict=2048,
            stop = ["STOP-GENERATION"]
            # num_predict=8192
        )
        self.read_agent_dict(agent_dict)
        self.apply_permissions(tools_dict)
        # Create agent
        self.agent = create_agent(
            llm,
            tools=None if len(self.tools) == 0 else self.tools,
            system_prompt=self.system_prompt
        )

    def read_agent_dict(self, agent_dict: dict):
        self.name: str = agent_dict["name"]
        self.system_prompt: str = agent_dict["system_prompt"]
        self.can_read = bool(agent_dict.get("can_read"))
        self.can_write = bool(agent_dict.get("can_write"))
        self.can_commit = bool(agent_dict.get("can_commit"))
        self.can_decide = bool(agent_dict.get("can_decide"))

    def apply_permissions(self, tools_dict):
        self.tools = []
        if self.can_read or self.can_write:
            self.system_prompt = self.system_prompt + self.ia_tool_instruction
        if self.can_read:
            self.tools.extend(tools_dict["read_tools"])
            self.system_prompt = self.system_prompt + self.ia_read_instruct
        if self.can_write: 
            self.tools.extend(tools_dict["write_tools"])
            self.system_prompt = self.system_prompt + self.ia_replace_instruct
        if self.can_decide:
            self.tools.extend(tools_dict["decide_tools"])
            self.system_prompt = self.system_prompt + self.ia_decide_instruct

    def get_agent(self):
        print(f"cr: {self.can_read}, cw: {self.can_write}, cd: {self.can_decide}, cc: {self.can_commit}")
        return self.agent
    
    def __str__(self):
        text = \
        f"######################## AGENT ######################## \
        \n# name: {self.name} \
        \n# system_prompt: {self.system_prompt}"
        if self.can_read is not None: text = text + f"\n# con_read: {str(self.can_read)}"
        if self.can_write is not None: text = text + f"\n# can_write: {str(self.can_write)}"
        if self.can_decide is not None: text = text + f"\n# can_decide: {str(self.can_decide)} "
        if self.can_commit is not None: text = text + f"\n# can_commit: {str(self.can_commit)} "
        text = text + "\n########################################################"
        return text
