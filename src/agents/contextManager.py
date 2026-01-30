import os
from langchain.messages import AnyMessage, AIMessage, HumanMessage, SystemMessage

from data.job import Job
from agents.agents import Agents

class ContextManager:
    
    def __init__(self, agents: Agents):
        self.agents_messages: dict[str, list[tuple[str, str]]] = {}
        for agent_name in agents.get_names_list():
            self.agents_messages.update({agent_name: []})
    
    def get_all(self) -> list[tuple[str, str]]:
        context: list[tuple[str, str]] = []
        for agent_messages in list(self.agents_messages.values()):
            context.extend(agent_messages)
        return context

    def get_context(self, agents: list[str], agent_name: str) -> list[tuple[str, str]]:
        context: list[tuple[str, str]] = []
        if agents is None:
            return self.get_all()
        for agent_name in agents + [agent_name]:
            context.extend(self.agents_messages[agent_name])
        return context

    def add_response_messages(self, agent_name: str, response_messages: list[tuple[str, str]]):
        self.agents_messages[agent_name].extend(response_messages)

    def add_message(self, agent_name: str, role: str, text: str):
        self.agents_messages[agent_name].append((role, text))

    def reset_context(self, agent_name: str, title:str):
        self.agents_messages[agent_name] = []