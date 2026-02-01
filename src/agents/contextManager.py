from data.job import Job

class ContextManager:
    
    def __init__(self, job: Job):
        self.prompts_responses: dict[str, list[tuple[str, str]]] = {}
        for prompt_name in job.get_prompts_list():
            self.prompts_responses.update({prompt_name: []})
    
    def get_all(self) -> list[tuple[str, str]]:
        context: list[tuple[str, str]] = []
        for agent_messages in list(self.prompts_responses.values()):
            context.extend(agent_messages)
        return context

    def get_context(self, prompts: list[str], prompt_name: str) -> list[tuple[str, str]]:
        context: list[tuple[str, str]] = []
        if prompts is None:
            return self.get_all()
        for prompt_name in prompts + [prompt_name]:
            context.extend(self.prompts_responses[prompt_name])
        return context

    def add_response_messages(self, prompt_name: str, response_messages: list[tuple[str, str]]):
        self.prompts_responses[prompt_name].extend(response_messages)

    def add_message(self, prompt_name: str, role: str, text: str):
        self.prompts_responses[prompt_name].append((role, text))

    def reset_context(self, prompts_names: list[str]):
        if prompts_names is None: return
        for prompt_name in prompts_names:
            self.prompts_responses.pop(prompt_name)
            self.prompts_responses.update({prompt_name: []})