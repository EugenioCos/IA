import json

class Prompt:

    tools_usage_message = "Agisci da agente AI, agisci direttamente sul file originali attraverso i tool che hai a disposizione. "
    permit_end_message = "Usa il tool 'end_work' solo se sei sicuro di aver controllato (leggendo e verficando il contenuto dei file modificati) che il lavoro è finito. NON CHIEDERE IL PERMESSO O LA CONFERMA PER USARE IL TOOL 'end_work'. "
    
    def __init__(self, prompt: dict):
        self.title: str = prompt["title"]
        self.agent_name: str = prompt["agent"]
        self.text: str = prompt["text"]
        self.prompt = self.text
        self.think: bool = prompt["think"]
        self.commit = prompt.get("commit")
        self.permit_end = prompt.get("permit_end")
        self.can_decide = prompt.get("can_decide")
        self.next_on_fail = prompt.get("next_on_fail")
        self.reset_on_success = prompt.get("reset_on_success")
        self.reset_on_fail = prompt.get("reset_on_fail")
        self.context = prompt.get("context")
        self.tools = prompt.get("tools")
        if self.tools: self.text = self.tools_usage_message + self.text
        if self.permit_end: self.text = self.text + self.permit_end_message

    def __str__(self):
        text = \
        f"######################## PROMPT ######################## \
        \n# title: {self.title} \
        \n# agent_name: {self.agent_name} \
        \n# prompt: {self.prompt} \
        \n# think: {str(self.think)}"
        if self.context is not None: text = text + f"\n# context: {str(self.context)}"
        if self.tools is not None: text = text + f"\n# tools: {str(self.tools)}"
        if self.commit is not None: text = text + f"\n# commit: {str(self.commit)} "
        if self.next_on_fail is not None: text = text + f"\n# next_on_fail: {self.next_on_fail}"
        if self.reset_on_success is not None: text = text + f"\n# reset_on_success: {str(self.reset_on_success)}"
        if self.reset_on_fail is not None: text = text + f"\n# reset_on_fail: {str(self.reset_on_fail)}"
        if self.permit_end is not None: text = text + f"\n# permit_end: {str(self.permit_end)}"
        if self.can_decide is not None: text = text + f"\n# can_decide: {str(self.can_decide)}"
        text = text + "\n########################################################"
        return text
