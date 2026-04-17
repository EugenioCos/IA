class Context:
    
    def __init__(self):
        self.prompts_messages: dict[str, list[tuple[str, str]]] = {}
    
    def add_context(self, prompt_name: str, agent_messages: list[tuple[str, str]]):
        self.prompts_messages.update({prompt_name: agent_messages})
    
    def get_all(self) -> list[tuple[str, str]]:
        context: list[tuple[str, str]] = []
        for agent_messages in list(self.prompts_messages.values()):
            context.extend(agent_messages)
        return context

    def size(self):
        return len(self.prompts_messages)

    def get_context(self, prompts: list[str], prompt_name: str) -> list[tuple[str, str]]:
        context: list[tuple[str, str]] = []
        if prompts is None:
            return self.get_all()
        for prompt_name in prompts + [prompt_name]:
            try:
                context.extend(self.prompts_messages[prompt_name])
            except:
                pass # AI can generate wrong prompt title
        return context

    def add_messages(self, prompt_name: str, response_messages: list[tuple[str, str]]):
        self.prompts_messages[prompt_name].extend(response_messages)

    def add_message(self, prompt_name: str, role: str, text: str):
        self.prompts_messages[prompt_name].append((role, text))

    def reset_context(self, prompts_names: list[str]):
        if prompts_names is None: return
        try:
            for prompt_name in prompts_names:
                self.prompts_messages.pop(prompt_name)
                self.prompts_messages.update({prompt_name: []})
        except:
            pass # Contesto già cancellato, questo è un edge case del job permesso per migliore resilienza

    def summarize(self):
        summary = []
        for title, prompt_messages in self.prompts_messages.items():
            if len(prompt_messages) == 0: continue
            human_message = prompt_messages[0]
            assistant_messgae = prompt_messages[-1]
            summary.append([title, human_message, assistant_messgae])
        return summary
