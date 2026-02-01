import json

from data.settings import Settings
from data.prompt import Prompt

class Job:

    ia_approve_count = 0
    ia_reject_count = 0
    prompts: dict[str, Prompt] = {}
    prompts_order_int_key: dict[str, int] = {}
    prompts_order_title_key: dict[str, int] = {}
    current = 0

    def __init__(self, settings: Settings):
        try:
            data = json.load(open(f"jobs/{settings.job_name}.json", "r"))
        except Exception as e:
            raise Exception(f"Invalid job, Exception: {str(e)}")
        
        self.source = data["source"]
        self.numero_esecuzioni = data["executions_count"]
        for i, prompt_dict in enumerate(data["prompts"]):
            prompt =  Prompt(prompt_dict)
            self.prompts.update({prompt.title: prompt})
            self.prompts_order_title_key.update({prompt.title: i})
            self.prompts_order_int_key.update({i: prompt.title})

    def get_prompt(self):
        if(self.current >= len(self.prompts)):
            return None
        prompt_index = self.prompts_order_int_key[self.current]
        return self.prompts.get(prompt_index)
    
    def get_prompts_list(self):
        return list(self.prompts.keys())
    
    def next(self):
        self.current = self.current + 1
    
    def set_current(self, title: str):
        self.current = self.prompts_order_title_key[title]

    def reset(self):
        self.current = 0

    def end(self):
        self.current = 100000

    def add_vote(self, is_approve: bool):
        if is_approve: self.ia_approve_count = self.ia_approve_count + 1
        else: self.ia_reject_count = self.ia_reject_count + 1

    def has_decided(self) -> bool:
        return (self.ia_approve_count + self.ia_reject_count) > 0

    def get_decision(self) -> bool:
        print(f"Approvations_count: {self.ia_approve_count}, rejects_count: {self.ia_reject_count}")
        decision = self.ia_reject_count < self.ia_approve_count
        self.ia_approve_count = 0
        self.ia_reject_count = 0
        return decision
