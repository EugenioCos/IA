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
        self.decision_type = prompt.get("decision_type")
        self.next_on_fail = prompt.get("next_on_fail")
        self.next_on_success = prompt.get("next_on_success")
        self.reset_on_success = prompt.get("reset_on_success")
        self.reset_on_fail = prompt.get("reset_on_fail")
        self.context_prompts = prompt.get("context_prompts")
        self.tools = prompt.get("tools")
        if self.tools: self.text = self.tools_usage_message + self.text
        if self.decision_type == "end": self.text = self.text + self.permit_end_message
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
        if self.must_decide is not None: text = text + f"\n# must_decide: {str(self.must_decide)}"
        if self.decision_type is not None: text = text + f"\n# decision_type: {str(self.decision_type)}"
        if self.next_on_fail is not None: text = text + f"\n# next_on_fail: {self.next_on_fail}"
        if self.next_on_success is not None: text = text + f"\n# next_on_fail: {self.next_on_success}"
        if self.reset_on_success is not None: text = text + f"\n# reset_on_success: {str(self.reset_on_success)}"
        if self.reset_on_fail is not None: text = text + f"\n# reset_on_fail: {str(self.reset_on_fail)}"
        text = text + "\n########################################################"
        return text
