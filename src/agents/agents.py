import json

from agents.agentWrapper import AgentWrapper

class Agents:

    agents: dict[str, AgentWrapper] = {}

    def __init__(self, read_tools, write_tools):
        try:
            data = json.load(open(f"agents_settings.json", "r"))
        except Exception as e:
            raise Exception(f"Invalid agents_settings, Exception: {str(e)}")
        
        for agent_dict in data["agents"]:
            agent = AgentWrapper(agent_dict, read_tools, write_tools)
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