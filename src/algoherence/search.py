from typing import Type
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
import os
from langchain_community.tools.tavily_search import TavilySearchResults
from dotenv import load_dotenv

load_dotenv()

class SearchToolInput(BaseModel):
    query: str = Field(description="The query to search for on the web.")

class SearchTool(BaseTool):
    name: str = "web_search"
    description: str = "Searches the web for real-time information and news using Tavily Search API."
    args_schema: Type[BaseModel] = SearchToolInput

    def _run(self, query: str) -> str:
        if not os.getenv("TAVILY_API_KEY"):
            return "Error: Tavily API key not configured."
        search = TavilySearchResults(max_results=3)
        results = search.run(query)

        # Format results for the LLM
        formatted_results = ""
        for i, res in enumerate(results):
            formatted_results += f"\nResult {i+1}:\n"
            formatted_results += f"Source: {res['url']}\n"
            formatted_results += f"Content: {res['content']}\n"

        return formatted_results
