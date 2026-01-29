from io import TextIOWrapper

class Prompt:

    tools_usage_message = "Agisci da agente AI, agisci direttamente sul file originali attraverso i tool che hai a disposizione. "
    permit_end_message = "Usa il tool 'end_work' solo se sei sicuro di aver controllato che il lavoro è finito. CONTROLLA DI AVER SVOLTO EFFETTIVAMENTE IL LAVORO E TERMINA SOLO SE IL LAVORO è AL 100% TERMINATO. NON CHIEDERE IL PERMESSO O LA CONFERMA PER USARE IL TOOL 'end_work'. "
    
    def __init__(self, text: str, think: bool, commit: bool, permit_end, post_flow: int, context: list[bool], tools: bool):
        self.prompt = text
        self.text = text
        self.think = think
        self.commit = commit
        self.post_flow = post_flow
        self.permit_end = permit_end
        self.context = context
        self.tools = tools
        if tools: text = self.tools_usage_message + text

    def log_prompt(self, out: TextIOWrapper):
        out.writelines([
            "\n\n######################## PROMPT ########################",
            "\n# prompt: ", self.prompt,
            "\n# think: ", str(self.think),
            "\n# commit: ", str(self.commit),
            "\n# post_flow: ", str(self.post_flow),
            "\n# permit_end: ", str(self.permit_end),
            "\n# context: ", str(self.context),
            "\n# tools: ", str(self.tools),
            "\n########################################################\n"
        ])
        out.flush() 
        print(f"[PROMPT]: {self.prompt}")

    def get_message(self):
        return ("human", self.text)