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

import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
import os

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
def estimate_future_profit(ticker, shares, mean_frame, backtest_frame, investment_period=1):
    """
    Estimate future profit based on historical performance of a mean reversion strategy.

    Args:
    ticker (str): Stock ticker symbol.
    shares (int): Number of shares to buy.
    mean_frame (int): Time frame for calculating the mean.
    backtest_frame (int): Time frame for backtesting.
    investment_period (int): Future investment period in years for profit estimation. Default is 1 year.
    """
    # Fetch historical data
    start_date = '2018-08-01'
    end_date = '2024-02-24'
    stock_data = yf.download(ticker, start=start_date, end=end_date)['Close']

    # Calculate the rolling mean and the z-scores
    stock_data = pd.DataFrame(stock_data)
    mean_data = stock_data['Close'].rolling(window=mean_frame).mean()
    stock_data['returns'] = stock_data['Close'].pct_change()
    stock_data['z_score'] = (stock_data['Close'] - mean_data) / stock_data['Close'].rolling(window=mean_frame).std()

    # Determine entry and exit signals from z-scores
    percentiles = [5, 10, 50, 90, 95]
    z_scores = stock_data['z_score'].dropna()
    percentile_values = np.percentile(z_scores, percentiles)
    buy_threshold = percentile_values[1]
    sell_threshold = percentile_values[3]
    stock_data['Signal'] = np.where(stock_data['z_score'] > sell_threshold, -1, np.where(stock_data['z_score'] < buy_threshold, 1, 0))

    # Backtesting
    backtest_data = stock_data[-backtest_frame:].copy()
    backtest_data['Signal'] = backtest_data['Signal'].shift(1)
    backtest_data['StrategyReturn'] = backtest_data['Signal'] * backtest_data['returns']
    
    # Backtesting
    backtest_data = stock_data[-backtest_frame:].copy()
    backtest_data['Signal'] = backtest_data['Signal'].shift(1)
    backtest_data['StrategyReturn'] = backtest_data['Signal'] * backtest_data['returns']
    
    # Calculate cumulative returns for the strategy and buy-and-hold approach
    backtest_data['CumulativeStrategyReturn'] = (1 + backtest_data['StrategyReturn']).cumprod()
    backtest_data['CumulativeBuyHoldReturn'] = (1 + backtest_data['returns']).cumprod()

    # Plot the cumulative returns
    plt.figure(figsize=(10, 6))
    plt.plot(backtest_data['CumulativeStrategyReturn'], label='Mean Reversion Strategy')
    plt.plot(backtest_data['CumulativeBuyHoldReturn'], label='Buy and Hold')
    plt.title(f"Cumulative Returns: {ticker}")
    plt.xlabel('Date')
    plt.ylabel('Cumulative Returns')
    plt.legend()
    plt.grid(True)
    
    
    graph_dir = 'graph'
    # Ensure the 'graph' directory exists
    graph_dir = 'graph'
    if not os.path.exists(graph_dir):
        os.makedirs(graph_dir)
    
    # Save the plot to the 'graph' directory
    plt.savefig(f"{graph_dir}/{ticker}_cumulative_returns.png")
    plt.close()  # Close the plot


    # Ensure the 'table' directory exists
    table_dir = 'table'
    if not os.path.exists(table_dir):
        os.makedirs(table_dir)
    #calculate annual return
    annual_return = backtest_data['StrategyReturn'].mean() * 252  # Approximate trading days in a year

    # Estimate future profit
    estimated_annual_profit = annual_return * shares * stock_data['Close'].iloc[-1]  # Estimate based on the last closing price
    estimated_future_profit = estimated_annual_profit * investment_period

    print(f"Estimated future profit for {ticker} over {investment_period} year(s) with {shares} shares: ${estimated_future_profit:.2f}")

    # Export the backtest data to CSV
    csv_filename = f"{table_dir}/{ticker}_mean_reversion_backtest.csv"
    backtest_data.to_csv(csv_filename)
    print(f"Backtest data exported to {csv_filename}")
    
# Example usage
ticker = input('Enter stock ticker: ')
shares = int(input('Number of shares to buy: '))
mean_frame = int(input('Enter time frame for mean: '))
backtest_frame = int(input('Enter time frame for backtest: '))
estimate_future_profit(ticker, shares, mean_frame, backtest_frame)
