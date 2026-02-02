import json

from agents.agentWrapper import AgentWrapper

class Agents:

    agents: dict[str, AgentWrapper] = {}

    def __init__(self, agents_dict, tools_dict, llm):
        for agent_dict in agents_dict["agents"]:
            agent = AgentWrapper(agent_dict, tools_dict, llm)
            self.agents.update({agent.name: agent})

    # error only if the user writes a wrong agent name in the job
    def get_agent_wrapper(self, agent_name):
        try:
            return self.agents[agent_name]
        except Exception:
            print(f"[ERROR] Agent not found '{agent_name}'")
            exit()
    
    def get_names_list(self):
        return list(self.agents.keys())