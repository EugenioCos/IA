import re
from langchain_ollama import ChatOllama
from langchain.agents import create_agent
from langchain.messages import HumanMessage, AIMessage,  ToolMessage, AnyMessage

from writer import Writer

class AgentManager:
    llm = ChatOllama(
        model="qwen3:8b",
        temperature=0.,
        reasoning=False,
        num_predict=8192
        # other params...
    )

    ia_base_prompt = "Sei un agente ia esperto informatico preciso e affidabile. Hai il permesso e devi agire nell'ambiente reale, non parlì in chat quando puoi agire direttamente, puoi e devi elencare, leggere e correggere i file. "
    ia_replace_instruct = "Per correggere i file usi il tool 'replace_in_file'. Se hai problemi leggi il file che vuoi correggere e assicurati di sostituire codice effettivamente presente. "

    def create_agent(self, use_tools, think):
        self.llm.reasoning = think
        self.agent = create_agent(
            self.llm,
            tools=self.tools if use_tools else None,
            system_prompt=self.ia_base_prompt+self.ia_replace_instruct,
        )

    def __init__(self, tools, writer: Writer):
        self.tools = tools
        self.writer = writer

    def generate_response(self, messages: list[tuple[str, str]], think: bool, use_tools: bool):
        """Generate text using Ollama's API"""
        self.create_agent(use_tools, think)
        try:
            num_messages_before = len(messages)
            response = self.agent.invoke({"messages": messages})
            messages: list[AnyMessage] = response["messages"][num_messages_before:]
            text = ""
            for message in messages:
                if isinstance(message, ToolMessage):
                    continue
                text = text + "\n" + message.pretty_repr()
            no_think_text = text.split("<think>")[0] + text.split("</think>")[1]
            self.writer.write_in_response(no_think_text)
            return no_think_text
        except Exception as e:
            raise Exception(f"Error communicating with Ollama: {str(e)}")