import json

from data.job import Job

class OrchestratorAgent:

    def __init__(self, agents_dict: dict):
        self.orc_prompt_template = f"Available agents:\n{str(agents_dict)}"+"""\n
Current task state:
{
    "task": "[task]",
    "max-steps": 10,
    "current-step": [step],
    "last-five-actions": [history]
}

Decide the next action as JSON only.
Do not do too much at same time.
Be sure to validate work and check correctness before proceeding.
Respond ONLY with a VALID JSON."""

    def validate_prompt_dict(self, jobRunner, prompt_dict):
        agent_name = prompt_dict['agent']
        if not jobRunner.agents.agent_exists(agent_name): return False
        return True

    def call_orchestrator(self, jobRunner, sub_job: Job):
        while True:
            orc_response = jobRunner.call_agent(jobRunner.job, sub_job)
            try:
                prompt_dict = json.loads(orc_response[0][1].strip())
                if not self.validate_prompt_dict(jobRunner, prompt_dict): 
                    continue
                sub_job.add_prompt(prompt_dict)
                break
            except json.JSONDecodeError as e:
                print(f"[ERROR] Orchestrator response decoding error: {orc_response}")

    def run_orchestrator_agent(self, jobRunner):
        sub_job_dict = {"executions_count": 1, "prompts": []}
        sub_job = Job(sub_job_dict)
        self.call_orchestrator(jobRunner, sub_job)
        while(sub_job.get_prompt()):
            # Call sub-agent
            jobRunner.run_prompt(sub_job)
            # Call orchestrator
            self.call_orchestrator(jobRunner, sub_job)
        print("Multi agent prompt done")
