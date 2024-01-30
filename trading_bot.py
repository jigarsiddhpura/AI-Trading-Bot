from lumibot.traders import Trader
from lumibot.brokers import Alpaca
from lumibot.strategies import Strategy
from lumibot.backtesting import YahooDataBacktesting
from lumibot.entities import Asset
from alpaca_trade_api import REST
from timedelta import Timedelta

from datetime import datetime
import dotenv
import os
dotenv.load_dotenv()

API_KEY = os.environ['API_KEY']
SECRET_KEY = os.environ['SECRET_KEY']
ENDPOINT = "https://paper-api.alpaca.markets"

ALPACA_CREDS = {
    "API_KEY": API_KEY,
    "API_SECRET": SECRET_KEY,
    "PAPER" : True
}

class MLTrader(Strategy):
    # isLifeCycleMethod , this method is called only once , when strategy execution starts
    def initialize(self, symbol: str = "SPY", cash_at_risk: float = 0.6):
        self.sleeptime = '24H'
        self.symbol = symbol
        self.last_trade = None
        self.cash_at_risk = cash_at_risk
        self.api = REST(key_id=API_KEY, secret_key=SECRET_KEY, base_url=ENDPOINT)

    # dynamically adjusting the quantity to buy
    def position_sizing(self):
        last_price = self.get_last_price(asset=self.symbol)
        cash = self.get_cash()
        quantity = round((cash * self.cash_at_risk)  / last_price , 0)
        return last_price,cash,quantity
    
    def get_dates(self):
        today = self.get_datetime()
        three_days_prior = today - Timedelta(days = 3)
        print(today)
        print(three_days_prior)
        return today.strftime('%Y-%m-%d'), three_days_prior.strftime('%Y-%m-%d')
    
    def get_news(self):
        today , three_days_prior = self.get_dates()
        news = self.api.get_news(symbol=self.symbol, start=three_days_prior, end=today)
        # news = [eve.__dict__["_raw"]["headline"] for eve in news]
        news = [eve.headline for eve in news]
        return news


    # isLifeCycleMethod , all trading logic here
    def on_trading_iteration(self):
        last_price,cash,quantity = self.position_sizing()
        if cash > last_price:
            if self.last_trade is None:
                news = self.get_news()
                print(news)
                order = self.create_order(
                    asset = self.symbol,
                    quantity= quantity,
                    side="buy",
                    type="bracket",
                    stop_loss_price=last_price*.95,
                    take_profit_price=last_price*1.20
                )
                self.submit_order(order=order)
                self.last_trade = "buy"


backtesting_start_date = datetime(2023, 12, 1)
backtesting_end_date = datetime(2023, 12, 31)

broker = Alpaca(config=ALPACA_CREDS)
asset = Asset(symbol='SPY',asset_type='stock')
strategy = MLTrader(name='mlstrat', broker=broker, parameters={"symbol":asset.symbol,"cash_at_risk":0.5})
strategy.backtest(YahooDataBacktesting,
                  backtesting_start_date,
                  backtesting_end_date,
                  parameters={"symbol":asset.symbol,"cash_at_risk":0.5})
