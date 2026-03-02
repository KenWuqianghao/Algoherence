from typing import Type
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
import os
import yfinance as yf
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from dotenv import load_dotenv

load_dotenv()

ALPACA_KEY = os.getenv("ALPACA_KEY")
ALPACA_SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")

trading_cli = None
if ALPACA_KEY and ALPACA_SECRET_KEY:
    try:
        trading_cli = TradingClient(ALPACA_KEY, ALPACA_SECRET_KEY, paper=True)
    except Exception as e:
        print(f"Error initializing Alpaca TradingClient: {e}")

class BuyStockInput(BaseModel):
    ticker: str = Field(description="Ticker of stock to buy")
    amount: int = Field(description="Amount of stock to buy")

class BuyStockTool(BaseTool):
    name: str = "buy_stock"
    description: str = "Buys a specified amount of a stock using the Alpaca API."
    args_schema: Type[BaseModel] = BuyStockInput

    def _run(self, ticker: str, amount: int) -> str:
        if not trading_cli:
            return "Error: Alpaca credentials not configured."
        try:
            market_order_data = MarketOrderRequest(
                symbol=ticker.upper(),
                qty=amount,
                side=OrderSide.BUY,
                time_in_force=TimeInForce.DAY
            )
            market_order = trading_cli.submit_order(order_data=market_order_data)
            if market_order.status.name in ["ACCEPTED", "PENDING_NEW", "FILLED"]:
                return f"Successfully placed order to buy {amount} shares of {ticker}. Order ID: {market_order.id}"
            else:
                return f"Failed to place order. Status: {market_order.status.name}"
        except Exception as e:
            return f"Error buying stock: {str(e)}"

class SellStockInput(BaseModel):
    ticker: str = Field(description="Ticker of stock to sell")
    amount: int = Field(description="Amount of stock to sell")

class SellStockTool(BaseTool):
    name: str = "sell_stock"
    description: str = "Sells a specified amount of a stock using the Alpaca API."
    args_schema: Type[BaseModel] = SellStockInput

    def _run(self, ticker: str, amount: int) -> str:
        if not trading_cli:
            return "Error: Alpaca credentials not configured."
        try:
            market_order_data = MarketOrderRequest(
                symbol=ticker.upper(),
                qty=amount,
                side=OrderSide.SELL,
                time_in_force=TimeInForce.DAY
            )
            market_order = trading_cli.submit_order(order_data=market_order_data)
            if market_order.status.name in ["ACCEPTED", "PENDING_NEW", "FILLED"]:
                return f"Successfully placed order to sell {amount} shares of {ticker}. Order ID: {market_order.id}"
            else:
                return f"Failed to place order. Status: {market_order.status.name}"
        except Exception as e:
            return f"Error selling stock: {str(e)}"

class MeanReversionInput(BaseModel):
    ticker: str = Field(description="Stock ticker")
    shares: int = Field(description="Number of shares to simulate buying")
    mean_frame: int = Field(default=20, description="Time frame for calculating the moving average (default 20)")
    backtest_frame: int = Field(default=252, description="Number of trading days for backtesting (default 252)")
    investment_period: int = Field(default=1, description="Future investment period in years for profit estimation (default 1)")

class MeanReversionTool(BaseTool):
    name: str = "mean_reversion"
    description: str = "Performs a z-score mean reversion backtest on a stock and estimates future profit."
    args_schema: Type[BaseModel] = MeanReversionInput

    def _run(self, ticker: str, shares: int, mean_frame: int = 20, backtest_frame: int = 252, investment_period: int = 1) -> str:
        try:
            # Increased buffer to ensure enough data for rolling window
            end_date = datetime.now()
            start_date = end_date - timedelta(days=backtest_frame + mean_frame + 60)

            ticker = ticker.upper()
            stock_data = yf.download(ticker, start=start_date, end=end_date, progress=False)

            if stock_data.empty:
                return f"Error: No data found for ticker {ticker}."

            df = stock_data[['Close']].copy()
            df.columns = ['Close']

            df['RollingMean'] = df['Close'].rolling(window=mean_frame).mean()
            df['RollingStd'] = df['Close'].rolling(window=mean_frame).std()
            df['ZScore'] = (df['Close'] - df['RollingMean']) / df['RollingStd']
            df['Returns'] = df['Close'].pct_change()

            # Z-score strategy thresholds
            buy_threshold = -1.5
            sell_threshold = 1.5

            df['Signal'] = 0
            df.loc[df['ZScore'] < buy_threshold, 'Signal'] = 1
            df.loc[df['ZScore'] > sell_threshold, 'Signal'] = -1

            # Backtesting
            df_bt = df.dropna().tail(backtest_frame).copy()
            df_bt['StrategyReturn'] = df_bt['Signal'].shift(1) * df_bt['Returns']
            df_bt['CumStrategyReturn'] = (1 + df_bt['StrategyReturn'].fillna(0)).cumprod()
            df_bt['CumBuyHoldReturn'] = (1 + df_bt['Returns'].fillna(0)).cumprod()

            # Plotting
            plt.figure(figsize=(10, 6))
            plt.plot(df_bt.index, df_bt['CumStrategyReturn'], label='Mean Reversion Strategy')
            plt.plot(df_bt.index, df_bt['CumBuyHoldReturn'], label='Buy and Hold')
            plt.title(f"Cumulative Returns: {ticker}")
            plt.legend()
            plt.grid(True)

            graph_dir = 'graph'
            os.makedirs(graph_dir, exist_ok=True)
            plt.savefig(f"{graph_dir}/{ticker}_cumulative_returns.png")
            plt.close()

            # Calculation of results
            annual_return = df_bt['StrategyReturn'].mean() * 252
            last_price = df_bt['Close'].iloc[-1]
            estimated_annual_profit = annual_return * shares * last_price
            estimated_future_profit = estimated_annual_profit * investment_period

            table_dir = 'table'
            os.makedirs(table_dir, exist_ok=True)
            df_bt.to_csv(f"{table_dir}/{ticker}_mean_reversion_backtest.csv")

            return (f"Mean Reversion Backtest for {ticker}:\n"
                    f"- Final Stock Price: ${last_price:.2f}\n"
                    f"- Estimated Annual Return (Strategy): {annual_return*100:.2f}%\n"
                    f"- Estimated profit over {investment_period} year(s) with {shares} shares: ${estimated_future_profit:.2f}")
        except Exception as e:
            return f"Error in mean reversion tool: {str(e)}"
