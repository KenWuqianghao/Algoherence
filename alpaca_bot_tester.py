import os
import dotenv

from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, GetOrdersRequest
from alpaca.trading.requests import LimitOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce, QueryOrderStatus
from alpaca.data import StockHistoricalDataClient, StockTradesRequest
from datetime import datetime


dotenv.load_dotenv()
ALPACA_KEY = os.environ["ALPACA_KEY"]
ALPACA_SECRET_KEY = os.environ["ALPACA_SECRET_KEY"]

trading_cli = TradingClient(ALPACA_KEY, ALPACA_SECRET_KEY, paper=True)
# data_cli = StockHistoricalDataClient("PKWP7PIJWJNRCM78Q38C", "imam9M5DEZafUD0OBPfvjhwpQbdbEErSubmj3ZNP")

# print(trading_cli.get_account().account_number)
# print(trading_cli.get_account().buying_power)

def buy_shares(ticker: str, amount: int) -> str:
    # CREATING AN ORDER
    market_order_data = MarketOrderRequest(
        symbol=ticker,
        qty=amount,
        side=OrderSide.BUY,
        time_in_force=TimeInForce.DAY
    )

    market_order = trading_cli.submit_order(order_data=market_order_data)

    print(market_order)
    print(market_order.status.name)


def sell_shares(ticker: str, amount: int) -> str:
    # CREATING AN ORDER
    market_order_data = MarketOrderRequest(
        symbol=ticker,
        qty=amount,
        side=OrderSide.SELL,
        time_in_force=TimeInForce.DAY
    )

    market_order = trading_cli.submit_order(order_data=market_order_data)

    print(market_order)
    print(market_order.status.name)


buy_shares("SPY", 1)
buy_shares("AAPL", 1)
buy_shares("MSFT", 1)
buy_shares("GME", 1)
sell_shares("NTDOY", 1)