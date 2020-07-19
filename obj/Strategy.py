# Other imports
import ta
import numpy as np

from obj.Trade import Trade
from obj.Data import Data


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

    def refresh(self, klines):
        for coin in self.tradeCoins:
            self.data[coin] = Data.process_raw_historic_data(klines[coin])
            self.calculate_indicator(coin)

        self.calculate_strategy()

    def calculate_indicator(self, coin):
        if self.indicator == 'MACD':
            macd = ta.trend.MACD(self.data[coin]["close"], n_fast=12, n_slow=26, n_sign=9)
            self.data[coin]["MACD"] = macd.macd()
            self.data[coin]["MACD_diff"] = macd.macd_diff()
            self.data[coin]["MACD_signal"] = macd.macd_signal()
            print(self.data[coin])
        elif self.indicator == 'RSI':
            self.data[coin]["RSI"] = ta.momentum.RSIIndicator(close=self.data[coin]["close"], n=14).rsi()
            print(self.data[coin])
        else: return None

    def calculate_strategy(self):
        if self.indicator == 'MACD':

            if self.strategy == 'CROSS':
                self.trades = []
                macdabove = False
                # For each time in klines, go through each trade coin
                for i in range(len(self.data[self.tradeCoins[-1]])):
                    for coin in self.tradeCoins:
                        if np.isnan(self.data[coin]["MACD"][i]) or np.isnan(self.data[coin]["MACD_signal"][i]): pass
                        # If both the MACD and signal are well defined, we compare the 2 and decide if a cross has occured
                        else:
                            if self.data[coin]["MACD"][i] > self.data[coin]["MACD_signal"][i]:
                                if (len(self.trades) == 0) or (self.trades[-1].action != "BUY"):
                                    if not macdabove:
                                        macdabove = True
                                        self.trades.append(Trade.new("BUY", self.baseCoin, coin, self.data[coin].loc[i, :]))
                                elif self.check_stop_loss(coin, self.data[coin].loc[i, :]):
                                    macdabove = False

                            elif (len(self.trades) > 0) and (self.trades[-1].trade_coin == coin):
                                if macdabove:
                                    macdabove = False
                                    self.trades.append(Trade.new("SELL", self.baseCoin, coin, self.data[coin].loc[i, :]))
            else: return None
        elif self.indicator == 'RSI':
            if self.strategy == '7030': return self.calculate_rsi(70, 30)
            elif self.strategy == '8020': return self.calculate_rsi(80, 20)
        else: return None

    def calculate_rsi(self, high, low):

        self.trades = []
        active_buy = False
        # Runs through each timestamp in order
        for i in range(len(self.data[self.tradeCoins[-1]])):
            for coin in self.tradeCoins:
                if np.isnan(self.data[coin]["RSI"][i]): pass
                # If the RSI is well defined, check if over high value or under low
                else:
                    if self.data[coin]["RSI"][i] < low and not active_buy:
                        if (len(self.trades) == 0) or (self.trades[-1].action != "BUY"):
                            self.trades.append(Trade.new("BUY", self.baseCoin, coin, self.data[coin].loc[i, :]))
                            active_buy = True
                    elif self.data[coin]["RSI"][i] > high and active_buy:
                        if (len(self.trades) > 0) and (self.trades[-1].trade_coin == coin):
                            self.trades.append(Trade.new("SELL", self.baseCoin, coin, self.data[coin].loc[i, :]))
                            active_buy = False
                    elif (self.check_stop_loss(coin, self.data[coin].loc[i, :])):
                        active_buy = False

    def check_stop_loss(self, coin, df):
        if (len(self.trades) > 0) and (self.trades[-1].action == "BUY") and (self.trades[-1].trade_coin == coin):
            sl_price = (self.trades[-1].price - (self.trades[-1].price * (self.stop_loss / 100)))
            if df["close"] < sl_price:
                self.trades.append(Trade.new("SELL", self.baseCoin, coin, df, f"Stop loss, price < {sl_price}"))
                return True
        return False
