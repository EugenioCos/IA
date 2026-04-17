from data.prompt import Prompt
from data.job import Job
from data.vote import Vote
from reporter import Reporter

class UserAgent:

    def __init__(self, reporter: Reporter, vote: Vote):
        self.prompt_text_template = "AGENT IS REQUESTING USER ACTION\n\n[request]"
        self.prompt_text_ask_response = "- provide a single response:"
        self.prompt_text_vote = "- type 'approve' to approve or 'reject' to reject:"
        self.prompt_text_vote_again = "error: invalid. Type 'approve' to approve or 'reject' to reject:"
        self.prompt_text_vote_reason = "- write the reason (optional)"
        self.reporter = reporter
        self.vote = vote

    def to_messages(self, prompt: str, user_response: str):
        prompt_message = ("assistant", prompt)
        user_message = ("user", user_response)
        return [prompt_message, user_message]
    
    def ask_vote(self):
        user_response = self.reporter.ask_to_user(self.prompt_text_vote)
        while True:
            if user_response[:7] == "approve":
                self.vote.add_vote(True)
                break
            elif user_response[:6] == "reject":
                self.vote.add_vote(False)
                break
            user_response = self.reporter.ask_to_user(self.prompt_text_vote_again)
        user_response = self.reporter.ask_to_user(self.prompt_text_vote_reason)
        return user_response
        
    def run_user_agent(self, job: Job):
        prompt = job.get_prompt()
        if prompt.must_decide:
            user_response = self.ask_vote()
        else:
            full_prompt = self.prompt_text_template.replace("[request]", prompt.text)
            user_response = self.reporter.ask_to_user(full_prompt)
        response_messages = self.to_messages(prompt.title, user_response)
        job.context.add_context(prompt.title, response_messages)
        print("User prompt done")
