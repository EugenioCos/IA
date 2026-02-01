from langchain_ollama import ChatOllama
from langchain.messages import HumanMessage, AIMessage,  ToolMessage, SystemMessage, AnyMessage

from writer import Writer
from workspace import Workspace
from data.job import Job
from data.prompt import Prompt
from agents.agents import Agents
from agents.contextManager import ContextManager

class AgentManager:
    llm = ChatOllama(
        model="qwen3:8b",
        temperature=0.1,
        reasoning=False,
        num_predict=8192
        # other params...
    )

    def __init__(self, 
                 writer: Writer, 
                 job: Job,
                 read_tools: list[function], 
                 write_tools: list[function], 
                 end_work_tool: function,
                 decide_tools: list[function]
            ):
        self.end_work_tool = end_work_tool
        self.decide_tools = decide_tools
        self.writer = writer
        self.job = job
        self.agents = Agents(read_tools, write_tools)
        self.context_manager = ContextManager(self.job)

    def select_agent(self, prompt: Prompt):
        agentWrapper = self.agents.get_agent_wrapper(prompt.agent_name)
        extra_tools = [] 
        if prompt.permit_end: extra_tools.append(self.end_work_tool)
        if prompt.can_decide: extra_tools = extra_tools + self.decide_tools
        return agentWrapper.get_agent(prompt, self.llm, extra_tools)
    
    def filter_tool_calls(self, tool_calls):
        filtered = [tool_call for tool_call in tool_calls if tool_call["name"] == 'replace_in_file']
        return filtered if len(filtered) > 0 else None
    
    def remove_reasoning(self, text: str) -> str:
        if "<think>" in text and "</think>" in text:
           return text.split("<think>")[0] + text.split("</think>")[1]
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
    
    def generate_context(self, writer: Writer, prompt: Prompt) -> list[tuple[str, str]]:
        writer.log_prompt_in_response(prompt)
        self.context_manager.add_message(prompt.title, "human", prompt.text)
        context = self.context_manager.get_context(prompt.context_prompts, prompt.title)
        writer.log_context(prompt.title, context)
        return context

    def generate_response(self, writer: Writer, messages: list[AnyMessage], prompt: Prompt) -> list[tuple[str,str]]:
        """Generate text using Ollama's API"""
        try_count = 0 # casi isolati di connessione instabile
        while(True):
            try:
                num_messages_before = len(messages)
                agent = self.select_agent(prompt)
                response = agent.invoke({"messages": messages})
                response_messages: list[AnyMessage] = response["messages"][num_messages_before:]
                filtered_response_messages = self.filter_response(response_messages, prompt.think)
                writer.write_messages_in_response(filtered_response_messages, prompt.think)
                return filtered_response_messages
            except KeyboardInterrupt as e:
                exit()
            except Exception as e:
                print(f"Error communicating with Ollama: {str(e)}")
                try_count = try_count + 1
                if try_count == 2: exit()
            
    def prompt_failed(self, prompt: Prompt):
        self.job.go_back(prompt.next_on_fail)
        self.context_manager.reset_context(prompt.reset_on_fail)
            
    def chat(self, writer: Writer, workspace: Workspace):
        while self.job.get_prompt():
            # Preparazione contesto e prompt
            prompt = self.job.get_prompt()
            context = self.generate_context(writer, prompt)
            # Risposta
            resp_messages = self.generate_response(writer, context, prompt)
            self.context_manager.add_response_messages(prompt.title, resp_messages)
            print("Prompt done")
            # Controllo per fail esplicito
            if prompt.can_decide and not self.job.get_decision():
                self.prompt_failed(prompt)
                continue
            # Controllo per segnale di fine job
            has_edited = workspace.commit("update")
            if prompt.permit_end and not has_edited: # controllo fine flusso
                if not self.job.ia_wants_terminate:
                    self.prompt_failed(prompt)
                    continue
                else:
                    self.job.ia_wants_terminate = False
            # Controllo modifiche mancanti o inaspettate
            if prompt.commit is not None and has_edited != prompt.commit: # controllo modifiche
                if(prompt.commit): message_text = "NON HAI MODIFICATO I FILE, RIPROVA UTILIZZANDO I TOOL CHE HAI A DISPOSIZIONE. PROVA A LEGGERE I FILE ORIGINAL E SOTITUIRE PORZIONI DI CODICE PIù BREVI SE NON RIESCI A USARE IL TOOL 'replace_in_file'"
                else: message_text = "HAI MODIFICATO FILE, QUINDI SERVONO ULTERIORI CONTROLLI"
                print(f"[SYSTEM] {message_text}")
                self.context_manager.add_message(prompt.title, "system", message_text)
                self.prompt_failed(prompt)
                continue
            # Controllo reset_on_success
            self.context_manager.reset_context(prompt.reset_on_success)
            # Tutto come previsto
            self.job.next()

