import json

class Prompt:

    tools_usage_message = "Agisci da agente AI, agisci direttamente sul file originali attraverso i tool che hai a disposizione. "
    permit_end_message = "Approve or reject the request to end the work."
    must_decide_message = "YOU MUST USE 'approve' OR 'reject' TOOLS."
    
    def __init__(self, prompt: dict):
        self.title: str = prompt["title"]
        self.agent_name: str = prompt["agent"]
        self.text: str = prompt["text"]
        self.prompt = self.text
        self.think: bool = prompt["think"]
        self.commit = prompt.get("commit")
        self.must_decide = prompt.get("must_decide")
        self.permit_end = prompt.get("permit_end")
        self.next_on_fail = prompt.get("next_on_fail")
        self.reset_on_success = prompt.get("reset_on_success")
        self.reset_on_fail = prompt.get("reset_on_fail")
        self.context_prompts = prompt.get("context_prompts")
        self.tools = prompt.get("tools")
        if self.tools: self.text = self.tools_usage_message + self.text
        if self.permit_end: self.text = self.text + self.permit_end_message
        if self.must_decide: self.text = self.text + self.must_decide_message

    def __str__(self):
        text = \
        f"######################## PROMPT ######################## \
        \n# title: {self.title} \
        \n# agent_name: {self.agent_name} \
        \n# prompt: {self.prompt} \
        \n# think: {str(self.think)}"
        if self.context_prompts is not None: text = text + f"\n# context_prompts: {str(self.context_prompts)}"
        if self.tools is not None: text = text + f"\n# tools: {str(self.tools)}"
        if self.commit is not None: text = text + f"\n# commit: {str(self.commit)} "
        if self.next_on_fail is not None: text = text + f"\n# next_on_fail: {self.next_on_fail}"
        if self.reset_on_success is not None: text = text + f"\n# reset_on_success: {str(self.reset_on_success)}"
        if self.reset_on_fail is not None: text = text + f"\n# reset_on_fail: {str(self.reset_on_fail)}"
        if self.permit_end is not None: text = text + f"\n# permit_end: {str(self.permit_end)}"
        text = text + "\n########################################################"
        return text
