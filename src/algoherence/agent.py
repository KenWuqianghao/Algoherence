from typing import Annotated, TypedDict, List
from langchain_cohere import ChatCohere
from langchain_core.messages import BaseMessage, HumanMessage, ToolMessage
from langgraph.graph import StateGraph, END
from .tools import BuyStockTool, SellStockTool, MeanReversionTool
from .search import SearchTool
from dotenv import load_dotenv

load_dotenv()

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], lambda x, y: x + y]

class TradingAgent:
    def __init__(self, model_name: str = "command-r"):
        self.llm = ChatCohere(model=model_name, temperature=0)
        self.tools = [BuyStockTool(), SellStockTool(), MeanReversionTool(), SearchTool()]
        self.tools_dict = {tool.name: tool for tool in self.tools}
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        self.workflow = self._create_workflow()
        self.app = self.workflow.compile()

    def _create_workflow(self):
        workflow = StateGraph(AgentState)

        workflow.add_node("agent", self._call_model)
        workflow.add_node("action", self._call_tool)

        workflow.set_entry_point("agent")

        workflow.add_conditional_edges(
            "agent",
            self._should_continue,
            {
                "continue": "action",
                "end": END,
            },
        )

        workflow.add_edge("action", "agent")

        return workflow

    def _should_continue(self, state):
        messages = state["messages"]
        last_message = messages[-1]
        if last_message.tool_calls:
            return "continue"
        else:
            return "end"

    def _call_model(self, state):
        messages = state["messages"]
        response = self.llm_with_tools.invoke(messages)
        return {"messages": [response]}

    def _call_tool(self, state):
        messages = state["messages"]
        last_message = messages[-1]

        tool_outputs = []
        for tool_call in last_message.tool_calls:
            tool = self.tools_dict[tool_call["name"]]
            response = tool.invoke(tool_call["args"])
            tool_outputs.append(
                ToolMessage(
                    tool_call_id=tool_call["id"],
                    content=str(response),
                )
            )
        return {"messages": tool_outputs}

    def query(self, input_str: str, chat_history: List[BaseMessage] = None):
        if chat_history is None:
            chat_history = []

        inputs = {"messages": chat_history + [HumanMessage(content=input_str)]}
        result = self.app.invoke(inputs)
        return result
