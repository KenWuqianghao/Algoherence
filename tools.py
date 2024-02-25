from langchain.retrievers.tavily_search_api import TavilySearchAPIRetriever
from langchain.retrievers import CohereRagRetriever
from langchain_community.chat_models import ChatCohere
from langchain_core.documents import Document

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
    return "\nObservation: {} shares of {} is BOUGHT. ACTION COMPLETED\n".format(amount, ticker)

@tool
def sell_stock(ticker: str, amount: int) -> int:
    """Sells a stock

    Args:
        ticker: Ticker of stock to sell
        amount: Amount of stock to sell
    """
    return "\nObservation: {} shares of {} is SOLD. ACTION COMPLETED.\n".format(amount, ticker)

@tool
def mean_reversion(ticker: str, amount: int) -> int:
    """Mean reversion strategy

    Args:
        ticker: Ticker of stock to buy
        amount: Amount of stock to buy
    """
    return "\nObservation: Mean reversion strategy for {} is EXECUTED. The strategy made a profit of 100 dollars. ACTION COMPLETED.\n".format(ticker)