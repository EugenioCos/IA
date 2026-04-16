from agents.agentWrapper import AgentWrapper

class Agents:

    orchestrator_dict = {
        "name": "multi-agent",
        "system_prompt": """
        You are ORCHESTRATOR, a supervisor coordinating a team of AI agents and tools. 
        You NEVER solve the task directly. You ONLY decide the next action.
        You must orchestrate the actions considering only this tools (can't create files):
        - can_read -> list_tool and read_file_tool
        - can_write -> replace_in_file_tool
        - can_decide -> approve_tool and reject_tool
        You orchestrate small size models.
        You must ALWAYS respond with a single JSON object using this parameters: 
        - title: str, reference for the prompt.
        - text: str, text of the prompt.
        - agent: str, the name of the agent to invoke.
        - context_prompts: list[str], list of prompts titles in the history to be used as context.
        - think: bool, if true thinking is added to the context.
        - commit: bool or null, true -> commit changes | false -> no file changes expected.
        - must_decide: true if ai must decide something.
        - decision_type: str or null, "end" -> program is terminated on reject | "undo_change" -> undo last commit on reject
        A single prompt can't include both decision and changes.
        If task is done use decision_type = "end" in a decide action.""",
    }

    def __init__(self, agents_dict: dict, tools_dict: dict, orchestrator_agent_model: str, model: str):
        self.dict = agents_dict
        self.agents: dict[str, AgentWrapper] = {}
        self.orchestrator = AgentWrapper(self.orchestrator_dict, None, orchestrator_agent_model)
        for agent_dict in agents_dict["agents"]:
            agent = AgentWrapper(agent_dict, tools_dict, model)
            self.agents.update({agent.name: agent})

    # error only if the user writes a wrong agent name in the job
    def get_agent_wrapper(self, agent_name):
        if agent_name == "multi-agent":
            return self.orchestrator
        try:
            return self.agents[agent_name]
        except Exception:
            print(f"[ERROR] Agent not found '{agent_name}'")
            exit()
    
    def get_names_list(self):
        return list(self.agents.keys())
    
    def agent_exists(self, agent_name: str):
        return agent_name in self.get_names_list()
