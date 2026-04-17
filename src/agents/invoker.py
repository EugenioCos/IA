from langchain.messages import HumanMessage, AIMessage,  ToolMessage, SystemMessage, AnyMessage

class Invoker:

    def filter_response(self, response_messages: list[AnyMessage], think: bool) -> list[str, str]:
        filtered: list[str, str] = []
        for message in response_messages:
            if isinstance(message, AIMessage):
                if message.content is None or message.content in ["", " "]: continue
                if think:
                    filtered.append(("assistant", message.content))
                else:
                    filtered.append(("assistant", message.pretty_repr()))
            elif isinstance(message, ToolMessage):
                continue
            elif isinstance(message, HumanMessage):
                filtered.append(("human", message.pretty_repr()))
            elif isinstance(message, SystemMessage):
                filtered.append(("system", message.pretty_repr()))
            else:
                raise Exception("invalid message type in filter_response")
        return filtered
    
    def invoke(self, agent, messages):
        try_count = 1
        while True:
            try:
                return agent.invoke(messages)
            except Exception as e:
                print(f"GENERATION ERROR {try_count}... ")
                try_count += 1
                if try_count > 2: raise e

    def generate_response(self, agent, messages: list[AnyMessage], think: bool) -> list[tuple[str,str]]:
        """Generate text using Ollama's API"""
        num_messages_before = len(messages)
        print("STARTED GENERATE... ")
        response = self.invoke(agent, {"messages": messages})
        print("ENDED GENERATE ")
        response_messages: list[AnyMessage] = response["messages"][num_messages_before:]
        filtered_response_messages = self.filter_response(response_messages, think)
        return filtered_response_messages