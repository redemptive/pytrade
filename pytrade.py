# Binance imports
from binance.client import Client
from binance.websockets import BinanceSocketManager

# Other imports
import talib as ta
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import os

class Strategy:

    def __init__(self, indicator_name, strategy_name, pair, interval, klines):
        #Name of indicator
        self.indicator = indicator_name
        #Name of strategy being used
        self.strategy = strategy_name
        #Trading pair
        self.pair = pair
        #Trading interval
        self.interval = interval
        #Kline data for the pair on given interval
        self.klines = klines
        #Calculates the indicator
        self.indicator_result = self.calculateIndicator()
        #Uses the indicator to run strategy
        self.strategy_result = self.calculateStrategy()


    '''
    Calculates the desired indicator given the init parameters
    '''
    def calculateIndicator(self):
        if self.indicator == 'MACD':
            close = [float(entry[4]) for entry in self.klines]
            close_array = np.asarray(close)

            macd, macdsignal, macdhist = ta.MACD(close_array, fastperiod=12, slowperiod=26, signalperiod=9)
            return [macd, macdsignal, macdhist]

        else:
            return None


    '''
    Runs the desired strategy given the indicator results
    '''
    def calculateStrategy(self):
        if self.indicator == 'MACD':

            if self.strategy == 'CROSS':
                open_time = [int(entry[0]) for entry in self.klines]
                new_time = [datetime.fromtimestamp(time / 1000) for time in open_time]
                self.time = new_time
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
                                cross = [new_time[i],self.indicator_result[0][i] , 'go', 'BUY', self.klines[i][4]]
                                crosses.append(cross)
                        else:
                            if macdabove == True:
                                macdabove = False
                                #Appends the timestamp, MACD value at the timestamp, color of dot, sell signal, and the sell price
                                cross = [new_time[i], self.indicator_result[0][i], 'ro', 'SELL', self.klines[i][4]]
                                crosses.append(cross)
                return crosses

            else:
                return None
        elif self.indicator == 'RSI':
            if self.strategy == '7030':
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
                        if float(self.indicator_result[i]) < 30 and active_buy == False:
                            # Appends the timestamp, RSI value at the timestamp, color of dot, buy signal, and the buy price
                            entry = [new_time[i], self.indicator_result[i], 'go', 'BUY', self.klines[i][4]]
                            result.append(entry)
                            active_buy = True
                        elif float(self.indicator_result[i]) > 70 and active_buy == True:
                            # Appends the timestamp, RSI value at the timestamp, color of dot, sell signal, and the sell price
                            entry = [new_time[i], self.indicator_result[i], 'ro', 'SELL', self.klines[i][4]]
                            result.append(entry)
                            active_buy = False
                return result
            elif self.strategy == '8020':
                open_time = [int(entry[0]) for entry in self.klines]
                new_time = [datetime.fromtimestamp(time / 1000) for time in open_time]
                self.time = new_time
                result = []
                active_buy = False
                # Runs through each timestamp in order
                for i in range(len(self.indicator_result)):
                    if np.isnan(self.indicator_result[i]):
                        pass
                    # If the RSI is well defined, check if over 80 or under 20
                    else:
                        if float(self.indicator_result[i]) < 20 and active_buy == False:
                            # Appends the timestamp, RSI value at the timestamp, color of dot, buy signal, and the buy price
                            entry = [new_time[i], self.indicator_result[i], 'go', 'BUY', self.klines[i][4]]
                            result.append(entry)
                            active_buy = True
                        elif float(self.indicator_result[i]) > 80 and active_buy == True:
                            # Appends the timestamp, RSI value at the timestamp, color of dot, sell signal, and the sell price
                            entry = [new_time[i], self.indicator_result[i], 'ro', 'SELL', self.klines[i][4]]
                            result.append(entry)
                            active_buy = False
                return result
        else:
            return None

    '''
    Getter for the strategy result
    '''
    def getStrategyResult(self):
        return self.strategy_result

    '''
    Getter for the klines
    '''
    def getKlines(self):
        return self.klines

    '''
    Getter for the trading pair
    '''
    def getPair(self):
        return self.pair

    '''
    Getter for the trading interval
    '''
    def getInterval(self):
        return self.interval

    '''
    Getter for the time list
    '''
    def getTime(self):
        return self.time

    '''
    Plots the desired indicator with strategy buy and sell points
    '''
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

        title = self.indicator + " Plot for " + self.pair + " on " + self.interval
        plt.title(title)
        plt.xlabel("Open Time")
        plt.ylabel("Value")
        plt.legend()
        plt.show()

class Backtest:
    def __init__(self, starting_amount, start_datetime, end_datetime, strategy):
        #Starting amount
        self.start = starting_amount
        #Number of trades
        self.num_trades = 0
        #Number of profitable trades
        self.profitable_trades = 0
        #Running amount
        self.amount = self.start
        #Start of desired interval
        self.startTime = start_datetime
        #End of desired interval
        self.endTime = end_datetime
        #Strategy object
        self.strategy = strategy
        #Trading pair
        self.pair = self.strategy.getPair()
        #Trading interval
        self.interval = self.strategy.getInterval()
        #Outputs the trades exectued
        self.trades = []
        #Runs the backtest
        self.results = self.runBacktest()
        #Prints the results
        self.printResults()


    def runBacktest(self):
        amount = self.start
        klines = self.strategy.getKlines()
        time = self.strategy.getTime()
        point_finder = 0
        strategy_result = self.strategy.getStrategyResult()
        #Finds the first cross point within the desired backtest interval
        while strategy_result[point_finder][0] < self.startTime:
            point_finder += 1
        #Initialize to not buy
        active_buy = False
        buy_price = 0
        #Runs through each kline
        for i in range(len(klines)):
            if point_finder > len(strategy_result)-1:
                break
            #If timestamp is in the interval, check if strategy has triggered a buy or sell
            if time[i] > self.startTime and time[i] < self.endTime:
                if(time[i] == strategy_result[point_finder][0]):
                    if strategy_result[point_finder][3] == 'BUY':
                        active_buy = True
                        buy_price = float(strategy_result[point_finder][4])
                        self.trades.append(['BUY', buy_price])
                    if strategy_result[point_finder][3] == 'SELL' and active_buy == True:
                        active_buy = False
                        bought_amount = amount / buy_price
                        self.num_trades += 1
                        if(float(strategy_result[point_finder][4]) > buy_price):
                            self.profitable_trades += 1
                        amount = bought_amount * float(strategy_result[point_finder][4])
                        self.trades.append(['SELL', float(strategy_result[point_finder][4])])
                    point_finder += 1
        self.amount = amount

    '''
    Prints the results of the backtest
    '''
    def printResults(self):
        print("Trading Pair: " + self.pair)
        print("Interval: " + self.interval)
        print("Ending amount: " + str(self.amount))
        print("Number of Trades: " + str(self.num_trades))
        profitable = self.profitable_trades / self.num_trades * 100
        print("Percentage of Profitable Trades: " + str(profitable) + "%")
        percent = self.amount / self.start * 100
        print(str(percent) + "% of starting amount")
        for entry in self.trades:
            print(entry[0] + " at " + str(entry[1]))

class Pytrade():
    def __init__(self):
        self.symbol:str = "ETHBTC"
        self.kline_interval:str = "15m"
        self.api_key:str = os.environ["BINANCE_API_KEY"]
        self.api_secret:str = os.environ["BINANCE_API_SECRET"]

        # Binance connection setup
        self.client = Client(self.api_key, self.api_secret)

        #self.open_ticker_socket(self.symbol)

        klines = self.client.get_klines(symbol=self.symbol,interval=self.kline_interval)

        macd_strategy = Strategy('MACD', 'CROSS', self.symbol, self.kline_interval, klines)
        macd_strategy.plotIndicator()
        time = macd_strategy.getTime()
        macd_backtest = Backtest(10000, time[0], time[len(time)-1], macd_strategy)

    def open_ticker_socket(self, symbol:str):
        self.bm = BinanceSocketManager(self.client)
        self.ticker_socket = self.bm.start_symbol_ticker_socket(symbol, self.process_message)
        self.bm.start()

    def process_message(self, msg):
        print("message type: {}".format(msg['e']))
        print(msg)

    def getBalances(self):
        prices = self.client.get_withdraw_history()
        return prices

if __name__ == '__main__':
    pytrade = Pytrade()