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
        temperature=0.,
        reasoning=False,
        num_predict=-8192
        # other params...
    )

    def __init__(self, 
                 writer: Writer, 
                 read_tools: list[function], 
                 write_tools: list[function], 
                 end_work_tool: function
            ):
        self.end_work_tool = end_work_tool
        self.writer = writer
        self.agents = Agents(read_tools, write_tools)
        self.context_manager = ContextManager(self.agents)

    def select_agent(self, prompt: Prompt):
        agentWrapper = self.agents.get_agent_wrapper(prompt.agent_name)
        extra_tools = [] if not prompt.permit_end else [self.end_work_tool]
        return agentWrapper.get_agent(prompt, self.llm, extra_tools)
    
    def filter_tool_calls(self, tool_calls):
        filtered = []
        for tool_call in tool_calls:
            if tool_call["name"] != 'replace_in_file': continue
            filtered.append(tool_call)
        return tool_calls if len(tool_calls) > 0 else None

    def filter_response(self, response_messages: list[AnyMessage]) -> list[str, str]:
        filtered: list[str, str] = []
        for message in response_messages:
            if isinstance(message, AIMessage):
                if message.tool_calls:
                    message.tool_calls = self.filter_tool_calls(message.tool_calls)
                    if message.tool_calls is None: continue
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
        try_count = 0 # casi isolati di connessione instabile
        while(True):
            try:
                num_messages_before = len(messages)
                agent = self.select_agent(prompt)
                response = agent.invoke({"messages": messages})
                response_messages: list[AnyMessage] = response["messages"][num_messages_before:]
                filtered_response_messages = self.filter_response(response_messages)
                return filtered_response_messages
            except Exception as e:
                print(f"Error communicating with Ollama: {str(e)}")
                try_count = try_count + 1
                if try_count == 2: exit()
                raise Exception("E")
            
    def chat(self, job: Job, writer: Writer, workspace: Workspace):
        for i in range(0, job.numero_esecuzioni):
            while job.get_prompt():
                # Preparazione contesto e prompt
                prompt = job.get_prompt()
                writer.log_prompt_in_response(prompt)
                self.context_manager.add_message(prompt.agent_name, "human", prompt.text)
                context = self.context_manager.get_context(prompt.context, prompt.agent_name)
                writer.log_context(context)
                # Risposta
                resp_messages = self.generate_response(context, prompt)
                writer.write_messages_in_response(resp_messages, prompt.think)
                self.context_manager.add_response_messages(prompt.agent_name, resp_messages)
                print("Prompt done")
                # Controlli post risposta
                has_edited = workspace.commit("update")
                if prompt.permit_end and not has_edited: # controllo fine flusso
                    if not job.ia_wants_terminate:
                        job.go_back(prompt.next_on_fail)
                    else: break
                else:
                    job.ia_wants_terminate = False
                if prompt.commit is not None and has_edited != prompt.commit: # controllo modifiche
                    if(prompt.commit): message_text = "NON HAI MODIFICATO I FILE, RIPROVA UTILIZZANDO I TOOL CHE HAI A DISPOSIZIONE. PROVA A LEGGERE I FILE ORIGINAL E SOTITUIRE PORZIONI DI CODICE PIù BREVI SE NON RIESCI A USARE IL TOOL 'replace_in_file'"
                    else: message_text = "HAI MODIFICATO FILE, QUINDI SERVONO ULTERIORI CONTROLLI"
                    print(f"[SYSTEM] {message_text}")
                    self.context_manager.add_message(prompt.agent_name, "system", message_text)
                    job.go_back(prompt.next_on_fail)
                    #self.context_manager.reset_context(prompt.agent_name)
                    continue
                job.next()