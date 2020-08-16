# Other imports
import ta
import numpy as np

from obj.Trade import Trade
from obj.Data import Data
from obj.MLEngine import MLEngine


class Strategy:

    def __init__(self, klines:dict, indicator_name:str, strategy:str, tradeCoins:list, baseCoin:str, interval:str, stop_loss:int):
        self.indicator:str = indicator_name
        self.strategy:str = strategy
        self.tradeCoins:str = tradeCoins
        self.baseCoin:str = baseCoin
        self.interval:str = interval
        self.stop_loss:str = stop_loss
        self.trades:list = []
        self.data:dict = {}
        self.refresh(klines)

    def filter_trades(self, trades):
        # Takes the trades from all trade coins and makes sure there is only one trade at once
        if trades:
            active_trade = False
            trades.sort(key=lambda x: x.time)
            for trade in trades:
                if not active_trade and trade.action == "BUY":
                    active_trade = True
                    self.trades.append(trade)
                elif active_trade and trade.trade_coin == self.trades[-1].trade_coin and trade.action == "SELL":
                    active_trade = False
                    self.trades.append(trade)

    def refresh(self, klines):
        trades = []
        for coin in self.tradeCoins:
            self.data[coin] = Data.process_raw_historic_data(klines[coin])
            self.calculate_indicator(coin)
            trades += self.calculate_strategy(self.data[coin], coin)

        self.filter_trades(trades)

    def calculate_indicator(self, coin):
        if self.indicator == "MACD":
            macd = ta.trend.MACD(self.data[coin]["close"], n_fast=12, n_slow=26, n_sign=9)
            self.data[coin]["MACD"] = macd.macd()
            self.data[coin]["MACD_diff"] = macd.macd_diff()
            self.data[coin]["MACD_signal"] = macd.macd_signal()
        elif self.indicator == "RSI":
            self.data[coin]["RSI"] = ta.momentum.RSIIndicator(close=self.data[coin]["close"], n=14).rsi()
        elif self.indicator == "STOCH":
            stoch = ta.momentum.StochasticOscillator(
                high=self.data[coin]["high"], low=self.data[coin]["low"], close=self.data[coin]["close"])
            self.data[coin]["STOCH"] = stoch.stoch()
            self.data[coin]["STOCH_signal"] = stoch.stoch_signal()
        elif self.indicator == "CLOUD":
            cloud = ta.trend.IchimokuIndicator(high=self.data[coin]["high"], low=self.data[coin]["low"])
            self.data[coin]["ichimoku_a"] = cloud.ichimoku_a()
            self.data[coin]["ichimoku_b"] = cloud.ichimoku_b()
            self.data[coin]["ichimoku_base_line"] = cloud.ichimoku_base_line()
            self.data[coin]["ichimoku_conversion_line"] = cloud.ichimoku_conversion_line()
        elif self.indicator == "ML":
            self.model = MLEngine("test")
        else: return None

    def calculate_strategy(self, df, coin):
        if self.indicator == 'MACD':
            if self.strategy == 'CROSS':
                trades = []
                active_buy = False
                for row in df.itertuples():
                    if np.isnan(row.MACD) or np.isnan(row.MACD_signal): pass
                    else:
                        if row.MACD > row.MACD_signal and not active_buy:
                            active_buy = True
                            trades.append(Trade.new("BUY", self.baseCoin, coin, row))
                        elif row.MACD < row.MACD_signal and active_buy:
                            active_buy = False
                            trades.append(Trade.new("SELL", self.baseCoin, coin, row))
                        elif trades and self.check_stop_loss(trades[-1].price, row.close):
                            trades.append(Trade.new("SELL", self.baseCoin, coin, row, "Stop loss"))
                            active_buy = False
                return trades
            else: return None
        elif self.indicator == "CLOUD":
            if self.strategy == "INORABOVE":
                trades = []
                active_buy = False
                above_cloud = False
                for row in df.itertuples():
                    if np.isnan(row.ichimoku_a) or np.isnan(row.ichimoku_b): pass
                    else:
                        if (row.close > row.ichimoku_a or row.close > row.ichimoku_b) and row.close > row.ichimoku_conversion_line and not active_buy:
                            active_buy = True
                            trades.append(Trade.new("BUY", self.baseCoin, coin, row))
                        elif (row.close < row.ichimoku_a or row.close < row.ichimoku_b) and active_buy and above_cloud:
                            active_buy = False
                            trades.append(Trade.new("SELL", self.baseCoin, coin, row))
                        elif (row.close < row.ichimoku_a and row.close < row.ichimoku_b) and active_buy:
                            active_buy = False
                            trades.append(Trade.new("SELL", self.baseCoin, coin, row))
                        elif trades and self.check_stop_loss(trades[-1].price, row.close):
                            trades.append(Trade.new("SELL", self.baseCoin, coin, row, "Stop loss"))
                            active_buy = False

                        if (row.close > row.ichimoku_a and row.close > row.ichimoku_b):
                            above_cloud = True
                        else:
                            above_cloud = False
                return trades
            elif self.strategy == "ABOVE":
                trades = []
                active_buy = False
                for row in df.itertuples():
                    if np.isnan(row.ichimoku_a) or np.isnan(row.ichimoku_b): pass
                    else:
                        if (row.close > row.ichimoku_a and row.close > row.ichimoku_b) and not active_buy:
                            active_buy = True
                            trades.append(Trade.new("BUY", self.baseCoin, coin, row))
                        elif not (row.close > row.ichimoku_a and row.close > row.ichimoku_b) and active_buy:
                            active_buy = False
                            trades.append(Trade.new("SELL", self.baseCoin, coin, row))
                return trades
        elif self.indicator == "STOCH":
            if self.strategy == "8020":
                trades = []
                active_buy = False
                above_high = False
                below_low = False
                for row in df.itertuples():
                    if np.isnan(row.STOCH_signal): pass
                    else:
                        if row.STOCH_signal < 20 and not below_low:
                            below_low = True
                        elif row.STOCH_signal > 80 and not above_high:
                            above_high = True
                        elif row.STOCH_signal > 20 and below_low:
                            below_low = False
                            if not active_buy:
                                active_buy = True
                                trades.append(Trade.new("BUY", self.baseCoin, coin, row))
                        elif row.STOCH_signal < 80 and above_high:
                            above_high = False
                            if active_buy:
                                active_buy = False
                                trades.append(Trade.new("SELL", self.baseCoin, coin, row))
                        elif trades and self.check_stop_loss(trades[-1].price, row.close):
                            trades.append(Trade.new("SELL", self.baseCoin, coin, row, "Stop loss"))
                            active_buy = False
                return trades
        elif self.indicator == "RSI":
            if self.strategy == "7030": return self.calculate_rsi(70, 30, df, coin)
            elif self.strategy == "8020": return self.calculate_rsi(80, 20, df, coin)
        elif self.indicator == "ML":
            return self.calculate_ml(df, coin)
        else: return None

    def calculate_ml(self, df, coin):
        active_buy = False
        predictions = self.model.predict(df)
        trades = []
        for row in df.itertuples(index=True):
            if row.Index < len(predictions):
                if not active_buy and predictions[row.Index][0] > row.close:
                    active_buy = True
                    trades.append(Trade.new("BUY", self.baseCoin, coin, row))
                elif active_buy and predictions[row.Index][0] < row.close:
                    active_buy = False
                    trades.append(Trade.new("SELL", self.baseCoin, coin, row))
                elif trades and self.check_stop_loss(trades[-1].price, row.close):
                    trades.append(Trade.new("SELL", self.baseCoin, coin, row, "Stop loss"))
                    active_buy = False
        return trades

    def calculate_rsi(self, high, low, df, coin):
        trades = []
        active_buy = False
        # Runs through each timestamp in order
        for row in df.itertuples():
            if np.isnan(row.RSI): pass
            else:
                if row.RSI < low and not active_buy:
                    trades.append(Trade.new("BUY", self.baseCoin, coin, row))
                    active_buy = True
                elif row.RSI > high and active_buy:
                    trades.append(Trade.new("SELL", self.baseCoin, coin, row))
                    active_buy = False
                elif trades and self.check_stop_loss(trades[-1].price, row.close):
                    trades.append(Trade.new("SELL", self.baseCoin, coin, row, "Stop loss"))
                    active_buy = False
        return trades

    def check_stop_loss(self, bought_price, current_price):
        sl_price = (bought_price - (bought_price * (self.stop_loss / 100)))
        if current_price < sl_price: return True
        else: return False
