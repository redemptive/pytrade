# Other imports
import talib as ta
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

from obj.Trade import Trade

class Strategy:

    def __init__(self, indicator_name:str, strategy_name:str, tradeCoins:list, baseCoin:str, interval:str, klines:dict, stop_loss:int):
        self.indicator = indicator_name
        self.strategy = strategy_name
        self.tradeCoins = tradeCoins
        self.baseCoin = baseCoin
        self.interval = interval
        self.klines = klines
        self.stop_loss = stop_loss
        self.time = {}
        self.trades = []

        self.highest_price:int = 0

        self.indicator_result = {}
        self.strategy_result = {}

        for coin in self.tradeCoins:
            self.indicator_result[coin] = self.calculate_indicator(coin)

        self.calculate_strategy()

    def set_time(self):
        open_time = {}
        self.time = {}

        for coin in self.tradeCoins:
            open_time[coin] = [int(entry[0]) for entry in self.klines[coin]]
            self.time[coin] = [datetime.fromtimestamp(time / 1000) for time in open_time[coin]]
            print(self.time[coin])

    def calculate_indicator(self, coin):
        if self.indicator == 'MACD':
            close_array = np.asarray([float(entry[4]) for entry in self.klines[coin]])
            macd, macdsignal, macdhist = ta.MACD(close_array, fastperiod=12, slowperiod=26, signalperiod=9)

            return [macd, macdsignal, macdhist]

        elif self.indicator == 'RSI':
            close = [float(entry[4]) for entry in self.klines[coin]]
            close_array = np.asarray(close)

            return ta.RSI(close_array, timeperiod=14)
        else: return None

    def calculate_strategy(self):
        if self.indicator == 'MACD':

            if self.strategy == 'CROSS':
                self.set_time()
                self.trades = []
                macdabove = False
                # For each time in klines, go through each trade coin
                for i in range(len(self.indicator_result[self.tradeCoins[-1]])):
                    for coin in self.tradeCoins:
                        if np.isnan(self.indicator_result[coin][0][i]) or np.isnan(self.indicator_result[coin][1][i]): pass
                        #If both the MACD and signal are well defined, we compare the 2 and decide if a cross has occured
                        else:
                            if self.indicator_result[coin][0][i] > self.indicator_result[coin][1][i]:
                                if (len(self.trades) == 0) or (self.trades[-1].action != "BUY"):
                                    if macdabove == False:
                                        macdabove = True
                                        self.trades.append(Trade(
                                            time=self.time[coin][i],
                                            base_coin=self.baseCoin,
                                            trade_coin=coin,
                                            action="BUY",
                                            price=self.klines[coin][i][4]
                                        ))
                                elif self.check_stop_loss(self.klines[coin][i], coin):
                                    macdabove = False

                            elif (len(self.trades) > 0) and (self.trades[-1].trade_coin == coin):
                                if macdabove == True:
                                    macdabove = False
                                    self.trades.append(Trade(
                                        time=self.time[coin][i],
                                        base_coin=self.baseCoin,
                                        trade_coin=coin,
                                        action="SELL",
                                        price=self.klines[coin][i][4]
                                    ))
            else: return None
        elif self.indicator == 'RSI':
            if self.strategy == '7030': return self.calculate_rsi(70, 30)
            elif self.strategy == '8020': return self.calculate_rsi(80, 20)
        else: return None

    def calculate_rsi(self, high, low):

        self.set_time()
        self.trades = []
        active_buy = False
        # Runs through each timestamp in order
        for i in range(len(self.indicator_result[self.tradeCoins[-1]])):
            for coin in self.tradeCoins:
                if np.isnan(self.indicator_result[coin][i]): pass
                # If the RSI is well defined, check if over high value or under low
                else:
                    if float(self.indicator_result[coin][i]) < low and active_buy == False:
                        if (len(self.trades) == 0) or (self.trades[-1].action != "BUY"):
                            # Appends the timestamp, RSI value at the timestamp, color of dot, buy signal, and the buy price
                            self.trades.append(Trade(
                                time=self.time[coin][i],
                                base_coin=self.baseCoin,
                                trade_coin=coin,
                                action="BUY",
                                price=self.klines[coin][i][4]
                            ))
                            active_buy = True
                    elif float(self.indicator_result[coin][i]) > high and active_buy == True:
                        if (len(self.trades) > 0) and (self.trades[-1].trade_coin == coin):
                            # Appends the timestamp, RSI value at the timestamp, color of dot, sell signal, and the sell price
                            self.trades.append(Trade(
                                time=self.time[coin][i],
                                base_coin=self.baseCoin,
                                trade_coin=coin,
                                action="SELL",
                                price=self.klines[coin][i][4]
                            ))
                            active_buy = False
                    elif (self.check_stop_loss(self.klines[coin][i], coin)):
                        active_buy = False

    def check_stop_loss(self, current_kline, coin):
        if (len(self.trades) > 0) and (self.trades[-1].action == "BUY") and (self.trades[-1].trade_coin == coin):
            if float(self.highest_price) < float(current_kline[4]):
                self.highest_price = current_kline[4]
            if ((float(current_kline[4]) / float(self.highest_price)) * 100) < (100 - self.stop_loss):
                self.trades.append(Trade(
                    time=datetime.fromtimestamp(current_kline[0] / 1000),
                    base_coin=self.baseCoin,
                    trade_coin=coin,
                    action="SELL",
                    price=current_kline[4]
                ))
                return True
        return False