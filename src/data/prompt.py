import json

class Prompt:

    tools_usage_message = "Agisci da agente AI, agisci direttamente sul file originali attraverso i tool che hai a disposizione. "
    permit_end_message = "Usa il tool 'end_work' solo se sei sicuro di aver controllato (leggendo e verficando il contenuto dei file modificati) che il lavoro è finito. NON CHIEDERE IL PERMESSO O LA CONFERMA PER USARE IL TOOL 'end_work'. "
    
    def __init__(self, prompt: dict):
        self.title: str = prompt["title"]
        self.text: str = prompt["text"]
        self.prompt = self.text
        self.think: bool = prompt["think"]
        self.commit = prompt.get("commit")
        self.permit_end = prompt.get("permit_end")
        self.next_on_fail = prompt.get("next_on_fail")
        self.reset_context = prompt.get("reset_context")
        self.context = prompt.get("context")
        self.tools = prompt.get("tools")
        if self.tools: self.text = self.tools_usage_message + self.text
        if self.permit_end: self.text = self.text + self.permit_end_message

    def __str__(self):
        return \
        f"######################## PROMPT ######################## \
        \n# prompt: {self.prompt} \
        \n# think: {str(self.think)} \
        \n# commit: {str(self.commit)} \
        \n# reset_context: {str(self.reset_context)} \
        \n# next_on_fail: {str(self.next_on_fail)} \
        \n# permit_end: {str(self.permit_end)} \
        \n# context: {str(self.context)} \
        \n# tools: {str(self.tools)} \
        \n########################################################"
