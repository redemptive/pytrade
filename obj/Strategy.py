# Other imports
import talib as ta
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

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

        self.indicator_result = {}
        self.strategy_result = {}

        for coin in self.tradeCoins:
            self.indicator_result[coin] = self.calculate_indicator(coin)
        
        self.strategy_result = self.calculate_strategy()

    def set_time(self):
        open_time = {}
        self.time = {}

        for coin in self.tradeCoins:
            open_time[coin] = [int(entry[0]) for entry in self.klines[coin]]
            self.time[coin] = [datetime.fromtimestamp(time / 1000) for time in open_time[coin]]

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
                
                crosses = []
                macdabove = False
                # For each time in klines, go through each trade coin
                for i in range(len(self.indicator_result[self.tradeCoins[0]][0])):
                    for coin in self.tradeCoins:
                        print(self.indicator_result[coin])
                        if np.isnan(self.indicator_result[coin][0][i]) or np.isnan(self.indicator_result[coin][1][i]): pass
                        #If both the MACD and signal are well defined, we compare the 2 and decide if a cross has occured
                        else:
                            if self.indicator_result[coin][0][i] > self.indicator_result[coin][1][i]:
                                if (len(crosses) == 0) or (crosses[-1][3] != "BUY"):
                                    if macdabove == False:
                                        macdabove = True
                                        #Appends the timestamp, MACD value at the timestamp, color of dot, buy signal, and the buy price
                                        crosses.append([self.time[coin][i], self.indicator_result[coin][0][i] , 'go', 'BUY', self.klines[coin][i][4], coin])
                            elif (len(crosses) > 0) and (crosses[-1][5] == coin):
                                if macdabove == True:
                                    macdabove = False
                                    #Appends the timestamp, MACD value at the timestamp, color of dot, sell signal, and the sell price
                                    crosses.append([self.time[coin][i], self.indicator_result[coin][0][i], 'ro', 'SELL', self.klines[coin][i][4], coin])
                                elif len(crosses) > 0:
                                    if (crosses[-1][3] == "BUY") and (crosses[-1][5] == coin):
                                        if (((float(self.klines[coin][i][4]) - float(crosses[-1][4])) / float(crosses[-1][4])) * 100 < -(self.stop_loss)):
                                            crosses.append([self.time[coin][i], self.indicator_result[coin][0][i], 'ro', 'SELL', self.klines[coin][i][4], coin])
                                            macdabove = False
                return crosses

            else:
                return None
        elif self.indicator == 'RSI':
            if self.strategy == '7030': return self.calculate_rsi(70, 30)
            elif self.strategy == '8020': return self.calculate_rsi(80, 20)
        else: return None

    def calculate_rsi(self, high, low):

        self.set_time()

        result = []
        active_buy = False
        # Runs through each timestamp in order
        for i in range(len(self.indicator_result[self.tradeCoins[-1]])):
            for coin in self.tradeCoins:
                if np.isnan(self.indicator_result[coin][i]): pass
                # If the RSI is well defined, check if over high value or under low
                else:
                    if float(self.indicator_result[coin][i]) < low and active_buy == False:
                        if (len(result) == 0) or (result[-1][3] != "BUY"):
                            # Appends the timestamp, RSI value at the timestamp, color of dot, buy signal, and the buy price
                            result.append([self.time[coin][i], self.indicator_result[coin][i], 'go', 'BUY', self.klines[coin][i][4], coin])
                            active_buy = True
                    elif float(self.indicator_result[coin][i]) > high and active_buy == True:
                        if (len(result) > 0) and (result[-1][5] == coin):
                            # Appends the timestamp, RSI value at the timestamp, color of dot, sell signal, and the sell price
                            result.append([self.time[coin][i], self.indicator_result[coin][i], 'ro', 'SELL', self.klines[coin][i][4], coin])
                            active_buy = False
                    elif len(result) > 0:
                        if (result[-1][3] == "BUY") and (result[-1][5] == coin):
                            if (((float(self.klines[coin][i][4]) - float(result[-1][4])) / float(result[-1][4])) * 100 < -(self.stop_loss)):
                                result.append([self.time[coin][i], self.indicator_result[coin][i], 'ro', 'SELL', self.klines[coin][i][4], coin])  
                                active_buy = False  

        return result