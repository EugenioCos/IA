import json

from agents.invoker import Invoker
from agents.userAgent import UserAgent
from reporter import Reporter
from data.job import Job
from data.prompt import Prompt
from data.vote import Vote
from agents.agents import Agents
from agents.orchestratorAgent import OrchestratorAgent

class JobRunner:

    def __init__(self, agents: Agents, reporter: Reporter, job: Job, vote: Vote):
        self.invoker = Invoker()
        self.agents = agents
        self.orchestratorAgent = OrchestratorAgent(agents.dict)
        self.userAgent = UserAgent(reporter, vote)
        self.reporter = reporter
        self.job = job
        self.vote = vote
    
    def generate_context(self, job: Job, sub_job: Job=None) -> list[tuple[str, str]]:
        prompt: Prompt = job.get_prompt()
        if sub_job is not None:
            job.context.reset_context([prompt.title])
            text = self.OrchestratorAgent.orc_prompt_template.replace("[task]", prompt.text)
            text = text.replace("[step]", str(sub_job.context.size()))
            text = text.replace("[history]", str(sub_job.context.summarize()))
        else: text = prompt.text
        job.context.add_message(prompt.title, "human", text)
        return job.context.get_context(prompt.context_prompts, prompt.title)
    
    def prompt_failed(self, job: Job, prompt: Prompt, message: str = None, keep_on_current: bool = False):
        if message is not None:
            print(f"[SYSTEM] {message}")
            job.context.add_message(prompt.title, "system", message)
        if not keep_on_current and prompt.next_on_fail is not None: job.set_current(prompt.next_on_fail)
        job.context.reset_context(prompt.reset_on_fail)

    def call_agent(self, job: Job, sub_job: Job=None):
        # Preparazione
        prompt: Prompt = job.get_prompt()
        self.reporter.log_prompt_in_response(prompt)
        context = self.generate_context(job, sub_job)
        agentWrapper = self.agents.get_agent_wrapper(prompt.agent_name)
        self.reporter.log_context(prompt.title, context)
        self.reporter.log_in_response(str(agentWrapper)) # log agent
        # Risposta
        resp_messages = self.invoker.generate_response(agentWrapper.get_agent(), context, prompt.think)
        job.context.add_messages(prompt.title, resp_messages)
        self.reporter.log_in_response(resp_messages) # log response
        print("Prompt done")
        return resp_messages
    
    def run_prompt(self, job: Job):
        prompt = job.get_prompt()
        if prompt.agent_name == "multi-agent":
            self.orchestratorAgent.run_orchestrator_agent(self)
        elif prompt.agent_name == "user":
            self.userAgent.run_user_agent(job)
        else:
            self.call_agent(job)
            self.apply_prompt_flow(job)

    def run_job(self):
        while self.job.get_prompt():
            self.run_prompt()
            self.job.next()

    def apply_prompt_flow(self, job: Job):
        prompt: Prompt = job.get_prompt()
        # - controllo decisione
        if prompt.must_decide:
            if not self.vote.has_decided():
                self.prompt_failed(job, prompt, "YOU MUST USE 'approve' OR 'reject' TOOLS TO DECIDE. LEGGI I FILE PER DECIDERE", True)
                return
            elif not self.vote.get_decision(): # Decisione false
                if prompt.decision_type == "undo_change":
                    self.reporter.revert_commit()
                else:
                    self.prompt_failed(job, prompt) # Decisione false porta a next_on_fail
                    return
            elif prompt.decision_type == "end": # Decisione true con permit_end attivo = richiesta terminazione
                job.end()
                return
        # - controllo modifiche mancanti o inaspettate
        elif prompt.commit is not None:
            has_edited = self.reporter.commit(prompt.title)
            if has_edited != prompt.commit:
                if(prompt.commit): self.prompt_failed(job, prompt, "NON HAI MODIFICATO I FILE, RIPROVA UTILIZZANDO I TOOL CHE HAI A DISPOSIZIONE. PROVA A LEGGERE I FILE ORIGINAL E SOTITUIRE PORZIONI DI CODICE PIù BREVI SE NON RIESCI A USARE IL TOOL 'replace_in_file'")
                else: self.prompt_failed(job, prompt, "HAI MODIFICATO FILE, QUINDI SERVONO ULTERIORI CONTROLLI")
                return
        # reset_on_success
        job.context.reset_context(prompt.reset_on_success)
        # prossimo prompt
        if prompt.next_on_success is not None: 
            job.set_current(prompt.next_on_success)
        else:
            job.next()
