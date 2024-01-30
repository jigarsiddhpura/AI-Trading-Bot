from lumibot.traders import Trader
from lumibot.brokers import Alpaca
from lumibot.strategies import Strategy
from lumibot.backtesting import YahooDataBacktesting
from lumibot.entities import Asset

from datetime import datetime
import dotenv
import os
dotenv.load_dotenv()

API_KEY = os.environ['API_KEY']
SECRET_KEY = os.environ['SECRET_KEY']

ALPACA_CREDS = {
    "API_KEY": API_KEY,
    "API_SECRET": SECRET_KEY,
    # "ENDPOINT": "https://paper-api.alpaca.markets"
    "PAPER" : True
}

class MLTrader(Strategy):
    # this method is called only once , when strategy execution starts
    def initialize(self, symbol: str = "SPY"):
        self.sleeptime = '24H'
        self.symbol = symbol
        self.last_trade = None

    # all trading logic here
    def on_trading_iteration(self):
        if self.last_trade is None:
            order = self.create_order(
                asset = self.symbol,
                quantity= 10,
                side="buy",
                type="market"
            )
            self.submit_order(order=order)
            self.last_trade = "buy"


backtesting_start_date = datetime(2023, 12, 1)
backtesting_end_date = datetime(2023, 12, 31)

broker = Alpaca(config=ALPACA_CREDS)
asset = Asset(symbol='SPY',asset_type='stock')
strategy = MLTrader(name='mlstrat', broker=broker, parameters={"symbol":asset.symbol})
strategy.backtest(YahooDataBacktesting,
                  backtesting_start_date,
                  backtesting_end_date,
                  parameters={"symbol":asset.symbol})
