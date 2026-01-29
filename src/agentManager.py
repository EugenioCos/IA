from typing import TypedDict
from langchain_ollama import ChatOllama
from langchain.agents import create_agent
from langchain.messages import HumanMessage, AIMessage,  ToolMessage

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

    def __init__(self, tools):
        self.tools = tools

    def generate_response(self, messages: list[tuple[str, str]], think: bool, use_tools: bool,  output):
        """Generate text using Ollama's API"""
        self.create_agent(use_tools, think)
        try:
            num_messages_before = len(messages)
            response = self.agent.invoke({"messages": messages})
            text = response["messages"][-1]#text = ""
            # for message in response["messages"][num_messages_before:]:
            #     if isinstance(message, ToolMessage):
            #         continue
            #     elif isinstance(message, AIMessage):
            #         if not message.content:
            #             #print("AIMessage Tool")
            #             continue
            #         #print("AIMessage")
            #         last_message=message.pretty_repr()
            #     elif isinstance(message, HumanMessage):
            #         continue
            #     else:
            #         print(type(message[1]))
            #         if not isinstance(message[1], str):
            #             continue
            #         last_message = message[1]
            #     text = text + "\n" + last_message
            output.write(text.content)
            output.flush()
            return text.content
        except Exception as e:
            raise Exception(f"Error communicating with Ollama: {str(e)}")