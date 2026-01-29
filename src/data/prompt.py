import json

class Prompt:

    tools_usage_message = "Agisci da agente AI, agisci direttamente sul file originali attraverso i tool che hai a disposizione. "
    permit_end_message = "Usa il tool 'end_work' solo se sei sicuro di aver controllato (leggendo e verficando il contenuto dei file modificati) che il lavoro è finito. NON CHIEDERE IL PERMESSO O LA CONFERMA PER USARE IL TOOL 'end_work'. "
    
    def __init__(self, prompt: json):
        self.text = prompt["text"]
        self.prompt = self.text
        self.think = prompt["think"]
        self.commit = prompt["commit"]
        self.delete_last_steps = prompt["delete_last_steps"]
        self.permit_end = prompt["permit_end"]
        self.post_flow = prompt["post_flow"]
        self.context = prompt["context"]
        self.tools = prompt["tools"]
        if self.tools: self.text = self.tools_usage_message + self.text
        if self.permit_end: self.text = self.text + self.permit_end_message

    def __str__(self):
        return \
        f"######################## PROMPT ######################## \
        \n# prompt: {self.prompt} \
        \n# think: {str(self.think)} \
        \n# commit: {str(self.commit)} \
        \n# delete_last_steps: {str(self.delete_last_steps)} \
        \n# post_flow: {str(self.post_flow)} \
        \n# permit_end: {str(self.permit_end)} \
        \n# context: {str(self.context)} \
        \n# tools: {str(self.tools)} \
        \n########################################################"
