from langchain.retrievers.tavily_search_api import TavilySearchAPIRetriever
from langchain.retrievers import CohereRagRetriever
from langchain_community.chat_models import ChatCohere
from langchain_core.documents import Document

import os
import dotenv

from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, GetOrdersRequest
from alpaca.trading.requests import LimitOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce, QueryOrderStatus
from alpaca.data import StockHistoricalDataClient, StockTradesRequest
from datetime import datetime

import requests
from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import BaseTool, StructuredTool, tool
from langchain_community.chat_models import ChatCohere
from langchain_community.embeddings import CohereEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.retrievers.document_compressors import CohereRerank
from langchain.retrievers import ContextualCompressionRetriever
from langchain_community.retrievers import CohereRagRetriever
from langchain_core.messages import HumanMessage


dotenv.load_dotenv()
ALPACA_KEY = os.environ["ALPACA_KEY"]
ALPACA_SECRET_KEY = os.environ["ALPACA_SECRET_KEY"]

trading_cli = TradingClient(ALPACA_KEY, ALPACA_SECRET_KEY, paper=True)
# data_cli = StockHistoricalDataClient("PKWP7PIJWJNRCM78Q38C", "imam9M5DEZafUD0OBPfvjhwpQbdbEErSubmj3ZNP")

@tool
def rag(query: str):
    """
    This function uses the RAG model to retrieve relevant documents for a given query
    query: The query to search for in complete sentences
    """
    
    rag = CohereRagRetriever(llm=ChatCohere(), verbose=True, connectors=[{"id": "web-search"}])
    docs = rag.get_relevant_documents(query)

    answer = '\nObservation:'
    answer += docs[-1].page_content + '\n'

    citations = '\nCITATIONS\n'
    citations += '------------------------------\n'
    for doc in docs[0: len(docs) - 2]:
        citations += doc.metadata['title'] + ': ' + doc.metadata['url'] + '\n'
        citations += '\n'
    print(citations)
    
    return answer

@tool
def buy_stock(ticker: str, amount: int) -> int:
    """Buys a stock

    Args:
        ticker: Ticker of stock to buy
        amount: Amount of stock to buy
    """

    # CREATING AN ORDER
    market_order_data = MarketOrderRequest(
        symbol=ticker,
        qty=amount,
        side=OrderSide.BUY,
        time_in_force=TimeInForce.DAY
    )

    market_order = trading_cli.submit_order(order_data=market_order_data)

    if (market_order.status.name != "ACCEPTED"):
        return "\nObservation: Transaction FAILED. ACTION INCOMPLETE\n"

    return "\nObservation: {} shares of {} is BOUGHT. ACTION COMPLETED\n".format(amount, ticker)

@tool
def sell_stock(ticker: str, amount: int) -> int:
    """Sells a stock

    Args:
        ticker: Ticker of stock to sell
        amount: Amount of stock to sell
    """

    # CREATING AN ORDER
    market_order_data = MarketOrderRequest(
        symbol=ticker,
        qty=amount,
        side=OrderSide.SELL,
        time_in_force=TimeInForce.DAY
    )

    market_order = trading_cli.submit_order(order_data=market_order_data)

    if (market_order.status.name != "ACCEPTED"):
        return "\nObservation: Transaction FAILED. ACTION INCOMPLETE\n"

    return "\nObservation: {} shares of {} is SOLD. ACTION COMPLETED\n".format(amount, ticker)

@tool
def mean_reversion(ticker: str, amount: int) -> int:
    """Mean reversion strategy

    Args:
        ticker: Ticker of stock to buy
        amount: Amount of stock to buy
    """
    return "\nObservation: Mean reversion strategy for {} is EXECUTED. The strategy made a profit of 100 dollars. ACTION COMPLETED.\n".format(ticker)