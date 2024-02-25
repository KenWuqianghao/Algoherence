from langchain import hub
from langchain.agents import AgentExecutor, create_react_agent
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.chat_models import ChatCohere
from langchain.retrievers.tavily_search_api import TavilySearchAPIRetriever
from langchain.retrievers import CohereRagRetriever
from langchain_community.chat_models import ChatCohere
from langchain_core.documents import Document
from langchain.agents import create_structured_chat_agent
from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import BaseTool, StructuredTool, tool
from tools import *
import langchain
from dotenv import load_dotenv
import os

import dotenv
dotenv.load_dotenv()

langchain.verbose=True

COHERE_API_KEY = os.environ["COHERE_API_KEY"]

class chatagent():
    def __init__(self):
        return
    
    def query(self, message: str, cfg, memory) -> str:
        cohere = ChatCohere(model="command", temperature = 0, streaming=True, verbose=True)
        tools = [buy_stock, sell_stock, mean_reversion, rag]
        prompt = hub.pull("kenwu/react-json")

        agent = create_structured_chat_agent(
            cohere,
            tools,
            prompt
        )
        
        # Create an agent executor by passing in the agent and tools
        agent_executor = AgentExecutor(
            agent=agent, 
            tools=tools,
            verbose=True,
            memory=memory,
            max_iterations=5,
            handle_parsing_errors=True,
            return_intermediate_steps=True
        )

        response = agent_executor.invoke({"input": message}, cfg, chat_history = [])
        return response