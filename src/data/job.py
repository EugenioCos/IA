import json

from data.prompt import Prompt
from data.context import Context

class Job:

    def __init__(self, job_dic):
        self.prompts: dict[str, Prompt] = {}
        self.prompts_order_int_key: dict[str, int] = {}
        self.prompts_order_title_key: dict[str, int] = {}
        self.current = 0
        self.numero_esecuzioni = job_dic["executions_count"]
        self.context = Context()
        for prompt_dict in job_dic["prompts"]:
            self.add_prompt(prompt_dict)

    # Prompts list

    def add_prompt(self, prompt_dict):
        prompt =  Prompt(prompt_dict)
        i = len(self.prompts)
        self.prompts.update({prompt.title: prompt})
        self.prompts_order_title_key.update({prompt.title: i})
        self.prompts_order_int_key.update({i: prompt.title})
        self.context.add_context(prompt.title, [])

    def get_prompt(self):
        if(self.current >= len(self.prompts)):
            return None
        prompt_index = self.prompts_order_int_key[self.current]
        return self.prompts.get(prompt_index)
    
    def get_prompts_list(self):
        return list(self.prompts.keys())
    
    # Flow control

    def next(self):
        self.current = self.current + 1
    
    def set_current(self, title: str):
        self.current = self.prompts_order_title_key[title]

    def reset(self):
        self.current = 0

    def end(self):
        self.current = 100000
