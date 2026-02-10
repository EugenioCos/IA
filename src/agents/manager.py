import os
from langchain_ollama import ChatOllama
#from langchain_openai import ChatOpenAI
from langchain.messages import HumanMessage, AIMessage,  ToolMessage, SystemMessage, AnyMessage

from reporter import Reporter
from data.job import Job
from data.prompt import Prompt
from agents.agents import Agents
from agents.contextManager import ContextManager

class AgentManager:

    def __init__(self, model, reporter: Reporter, job: Job, agents_dict, tools_dict):
        self.reporter = reporter
        self.job = job
        self.llm = ChatOllama(
            #model="kimi-k2.5:cloud",
            #model="gpt-oss:120b-cloud",
            model=model,
            reasoning=False,
            temperature=0.,
            num_ctx=4096,
            num_predict=4096,
            stop = ["STOP-GENERATION"]
            # num_predict=8192
            # other params...
        )
        self.agents = Agents(agents_dict, tools_dict, self.llm)
        self.context_manager = ContextManager(self.job)
    
    def filter_tool_calls(self, tool_calls):
        filtered = [tool_call for tool_call in tool_calls if tool_call["name"] == 'replace_in_file']
        return filtered if len(filtered) > 0 else None
    
    def remove_reasoning(self, text: str) -> str:
        if "<think>" in text:
            tmp: str = text.split("<think>", maxsplit=1)[0]
            if "</think>" in text:
               tmp = tmp + text.split("</think>", maxsplit=1)[1]
               return tmp
            else:
                return tmp
        else: return text

    def filter_response(self, response_messages: list[AnyMessage], think: bool) -> list[str, str]:
        filtered: list[str, str] = []
        for message in response_messages:
            if isinstance(message, AIMessage):
                if message.tool_calls:
                    message.tool_calls = self.filter_tool_calls(message.tool_calls)
                    if message.tool_calls is None: continue
                if think:
                    filtered.append(("assistant", message.pretty_repr()))
                else: 
                    text = self.remove_reasoning(message.pretty_repr())
                    filtered.append(("assistant", text))
            elif isinstance(message, ToolMessage):
                continue
            elif isinstance(message, HumanMessage):
                filtered.append(("human", message.pretty_repr()))
            elif isinstance(message, SystemMessage):
                filtered.append(("system", message.pretty_repr()))
            else:
                raise Exception("message type not found")
        return filtered
    
    def generate_context(self, prompt: Prompt) -> list[tuple[str, str]]:
        self.context_manager.add_message(prompt.title, "human", prompt.text)
        context = self.context_manager.get_context(prompt.context_prompts, prompt.title)
        return context

    def generate_response(self, agent, messages: list[AnyMessage], prompt: Prompt) -> list[tuple[str,str]]:
        """Generate text using Ollama's API"""
        num_messages_before = len(messages)
        print("STARTED GENERATE... ")
        try:
            response = agent.invoke({"messages": messages})
        except KeyboardInterrupt as e:
            exit()
        print("ENDED GENERATE ")
        response_messages: list[AnyMessage] = response["messages"][num_messages_before:]
        filtered_response_messages = self.filter_response(response_messages, prompt.think)
        self.reporter.write_in_response(filtered_response_messages)
        return filtered_response_messages
            
    def prompt_failed(self, prompt: Prompt, message: str = None, keep_on_current: bool = False):
        if message is not None:
            print(f"[SYSTEM] {message}")
            self.context_manager.add_message(prompt.title, "system", message)
        if not keep_on_current: self.job.set_current(prompt.next_on_fail)
        self.context_manager.reset_context(prompt.reset_on_fail)
            
    def chat(self):
        while self.job.get_prompt():
            # Preparazione
            prompt = self.job.get_prompt()
            context = self.generate_context(prompt)
            agentWrapper = self.agents.get_agent_wrapper(prompt.agent_name)
            self.reporter.log_prompt_in_response(prompt)
            self.reporter.log_context(prompt.title, context)
            self.reporter.write_in_response(str(agentWrapper)) # log agent
            # Risposta
            resp_messages = self.generate_response(agentWrapper.get_agent(), context, prompt)
            self.context_manager.add_response_messages(prompt.title, resp_messages)
            print("Prompt done")
            # Post Risposta
            has_edited = self.reporter.commit("update")
            # - controllo decisione
            if prompt.must_decide:
                if not self.job.has_decided():
                    self.prompt_failed(prompt, "YOU MUST USE 'approve' OR 'reject' TOOLS TO DECIDE. LEGGI I FILE PER DECIDERE", True)
                    continue
                elif not self.job.get_decision(): # Decisione false
                    if prompt.permit_end and not has_edited: # Decisione false con permit_end attivo = richiesta terminazione
                        self.job.end()
                        continue
                    self.prompt_failed(prompt) # Decisione false porta a next_on_surrent
                    continue
                elif prompt.permit_end: # Decisione true con permit_end attivo segue next_on_fail
                    self.prompt_failed(prompt, keep_on_current=True)

            # - controllo modifiche mancanti o inaspettate
            if prompt.commit is not None and has_edited != prompt.commit:
                if(prompt.commit): self.prompt_failed(prompt, "NON HAI MODIFICATO I FILE, RIPROVA UTILIZZANDO I TOOL CHE HAI A DISPOSIZIONE. PROVA A LEGGERE I FILE ORIGINAL E SOTITUIRE PORZIONI DI CODICE PIù BREVI SE NON RIESCI A USARE IL TOOL 'replace_in_file'")
                else: self.prompt_failed(prompt, "HAI MODIFICATO FILE, QUINDI SERVONO ULTERIORI CONTROLLI")
                continue
            # Controllo reset_on_success
            self.context_manager.reset_context(prompt.reset_on_success)
            # Tutto come previsto
            if prompt.next_on_success is not None: 
                self.job.set_current(prompt.next_on_success)
            else:
                self.job.next()

