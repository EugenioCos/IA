import json

from data.settings import Settings
from data.prompt import Prompt

class Job:

    ia_wants_terminate = False
    prompts: list[Prompt] = []
    current = 0

    def __init__(self, settings: Settings):
        try:
            data = json.load(open(f"jobs/{settings.job_name}.json", "r"))
        except Exception as e:
            raise Exception(f"Invalid job, Exception: {str(e)}")
        
        self.root = data["root"]
        for prompt in data["prompts"]:
            text = prompt["text"]
            think = prompt["think"]
            commit = prompt["commit"]
            permit_end = prompt["permit_end"]
            post_flow = prompt["post_flow"]
            context = prompt["context"]
            tools = prompt["tools"]
            self.prompts.append(Prompt(text, think, commit, permit_end, post_flow, context, tools))

    def get_prompt(self):
        if(self.current == len(self.prompts)):
            return None
        return self.prompts[self.current]
    
    def next(self):
        self.current = self.current + 1
    
    def go_back(self, diff):
        save = self.current
        while self.current - save != diff:
            self.current = self.current - 1
        

