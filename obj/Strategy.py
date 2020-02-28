# Other imports
import talib as ta
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

class Strategy:

    def __init__(self, indicator_name:str, strategy_name:str, pair:str, interval:str, klines):
        self.indicator = indicator_name
        self.strategy = strategy_name
        self.pair = pair
        self.interval = interval
        self.klines = klines
        self.indicator_result = self.calculate_indicator()
        self.strategy_result = self.calculate_strategy()

    def calculate_indicator(self):
        if self.indicator == 'MACD':
            close_array = np.asarray([float(entry[4]) for entry in self.klines])
            macd, macdsignal, macdhist = ta.MACD(close_array, fastperiod=12, slowperiod=26, signalperiod=9)

            return [macd, macdsignal, macdhist]

        elif self.indicator == 'RSI':
            close = [float(entry[4]) for entry in self.klines]
            close_array = np.asarray(close)

            return ta.RSI(close_array, timeperiod=14)
        else:
            return None

    def calculate_strategy(self):
        if self.indicator == 'MACD':

            if self.strategy == 'CROSS':
                open_time = [int(entry[0]) for entry in self.klines]
                self.time = [datetime.fromtimestamp(time / 1000) for time in open_time]
                crosses = []
                macdabove = False
                #Runs through each timestamp in order
                for i in range(len(self.indicator_result[0])):
                    if np.isnan(self.indicator_result[0][i]) or np.isnan(self.indicator_result[1][i]):
                        pass
                    #If both the MACD and signal are well defined, we compare the 2 and decide if a cross has occured
                    else:
                        if self.indicator_result[0][i] > self.indicator_result[1][i]:
                            if macdabove == False:
                                macdabove = True
                                #Appends the timestamp, MACD value at the timestamp, color of dot, buy signal, and the buy price
                                crosses.append([self.time[i],self.indicator_result[0][i] , 'go', 'BUY', self.klines[i][4]])
                        else:
                            if macdabove == True:
                                macdabove = False
                                #Appends the timestamp, MACD value at the timestamp, color of dot, sell signal, and the sell price
                                crosses.append([self.time[i], self.indicator_result[0][i], 'ro', 'SELL', self.klines[i][4]])
                return crosses

            else:
                return None
        elif self.indicator == 'RSI':
            if self.strategy == '7030':
                return self.calculateRsi(70, 30)
            elif self.strategy == '8020':
                return self.calculateRsi(80, 20)
        else:
            return None

    def calculateRsi(self, high, low):
        open_time = [int(entry[0]) for entry in self.klines]
        new_time = [datetime.fromtimestamp(time / 1000) for time in open_time]
        self.time = new_time
        result = []
        active_buy = False
        # Runs through each timestamp in order
        for i in range(len(self.indicator_result)):
            if np.isnan(self.indicator_result[i]):
                pass
            # If the RSI is well defined, check if over 70 or under 30
            else:
                if float(self.indicator_result[i]) < low and active_buy == False:
                    # Appends the timestamp, RSI value at the timestamp, color of dot, buy signal, and the buy price
                    result.append([new_time[i], self.indicator_result[i], 'go', 'BUY', self.klines[i][4]])
                    active_buy = True
                elif float(self.indicator_result[i]) > high and active_buy == True:
                    # Appends the timestamp, RSI value at the timestamp, color of dot, sell signal, and the sell price
                    result.append([new_time[i], self.indicator_result[i], 'ro', 'SELL', self.klines[i][4]])
                    active_buy = False

        return result

    def plotIndicator(self):
        open_time = [int(entry[0]) for entry in self.klines]
        new_time = [datetime.fromtimestamp(time / 1000) for time in open_time]
        plt.style.use('dark_background')
        for entry in self.strategy_result:
            plt.plot(entry[0], entry[1], entry[2])
        if self.indicator == 'MACD':
            plt.plot(new_time, self.indicator_result[0], label='MACD')
            plt.plot(new_time, self.indicator_result[1], label='MACD Signal')
            plt.plot(new_time, self.indicator_result[2], label='MACD Histogram')

        elif self.indicator == 'RSI':
            plt.plot(new_time, self.indicator_result, label='RSI')

        else:
            pass

        plt.title(f"{self.indicator} Plot for {self.pair} on {self.interval}")
        plt.xlabel("Open Time")
        plt.ylabel("Value")
        plt.legend()
        plt.show()