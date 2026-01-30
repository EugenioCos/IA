import re
from langchain_ollama import ChatOllama
from langchain.agents import create_agent
from langchain.messages import HumanMessage, AIMessage,  ToolMessage, SystemMessage, AnyMessage

from writer import Writer
from data.prompt import Prompt

class AgentManager:
    llm = ChatOllama(
        model="qwen3:8b",
        temperature=0.,
        reasoning=False,
        num_predict=-8192
        # other params...
    )

    ia_base_prompt = "Sei un agente ia esperto informatico preciso e affidabile. Hai il permesso e devi agire nell'ambiente reale, non parlì in chat quando puoi agire direttamente, puoi e devi elencare, leggere e correggere i file. "
    ia_replace_instruct = "Per correggere i file usi il tool 'replace_in_file'. Se hai problemi leggi il file che vuoi correggere e assicurati di sostituire codice effettivamente presente. "

    def create_agent(self, prompt: Prompt):
        self.llm.reasoning = prompt.think
        tools = self.tools
        if prompt.permit_end: tools.append(self.end_work_tool)
        self.agent = create_agent(
            self.llm,
            tools=tools if prompt.tools else None,
            system_prompt=self.ia_base_prompt+self.ia_replace_instruct,
        )

    def __init__(self, tools, end_work_tool: function, writer: Writer):
        self.tools = tools
        self.end_work_tool = end_work_tool
        self.writer = writer

    def filter_response(self, response_messages: list[AnyMessage]) -> list[str, str]:
        filtered: list[str, str] = []
        for message in response_messages:
            if isinstance(message, AIMessage):
                filtered.append(("assistant", message.pretty_repr()))
            elif isinstance(message, ToolMessage):
                continue
            elif isinstance(message, HumanMessage):
                filtered.append(("human", message.pretty_repr()))
            elif isinstance(message, SystemMessage):
                filtered.append(("system", message.pretty_repr()))
            else:
                raise Exception("message type not found")
        return filtered


    def generate_response(self, messages: list[AnyMessage], prompt: Prompt) -> list[tuple[str,str]]:
        """Generate text using Ollama's API"""
        self.create_agent(prompt)
        try_count = 0 # casi isolati di connessione instabile
        while(True):
            try:
                num_messages_before = len(messages)
                response = self.agent.invoke({"messages": messages})
                response_messages: list[AnyMessage] = response["messages"][num_messages_before:]
                filtered_response_messages = self.filter_response(response_messages)
                return filtered_response_messages
            except Exception as e:
                print(f"Error communicating with Ollama: {str(e)}")
                try_count = try_count + 1
                if try_count == 2: exit()