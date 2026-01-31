import json

from data.settings import Settings
from data.prompt import Prompt

class Job:

    ia_wants_terminate = False
    ia_failed = False
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
    
    def get_prompt_index(self, title: str):
        return self.prompts_order_title_key.get(title)
    
    def next(self):
        self.current = self.current + 1
    
    def go_back(self, title: str):
        self.current = self.prompts_order_title_key[title]
