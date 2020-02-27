# Binance imports
from binance.client import Client
from binance.websockets import BinanceSocketManager

# Other imports
import talib as ta
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import os
import argparse

class Strategy:

    def __init__(self, indicator_name, strategy_name, pair, interval, klines):
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

class Backtest:
    def __init__(self, starting_amount, start_datetime, end_datetime, strategy, verbose):
        self.verbose = verbose
        self.start = starting_amount
        self.num_trades = 0
        self.profitable_trades = 0
        self.amount = self.start
        self.startTime = start_datetime
        self.endTime = end_datetime
        self.strategy = strategy
        self.interval = self.strategy.interval
        self.trades = []
        self.runBacktest()
        self.printResults()


    def runBacktest(self):
        amount = self.start
        klines = self.strategy.klines
        time = self.strategy.time
        point_finder = 0
        strategy_result = self.strategy.strategy_result
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

    def printResults(self):
        print(f"\nTrading Pair: {self.strategy.pair}")
        print(f"Indicator: {self.strategy.indicator}")
        print(f"Strategy: {self.strategy.strategy}")
        print(f"Interval: {self.interval}")
        print(f"Ending amount: {str(self.amount)}")
        print(f"Number of Trades: {str(self.num_trades)}")
        if self.num_trades > 0:
            print(f"Percentage of Profitable Trades: {str(self.profitable_trades / self.num_trades * 100)}%")
        print(f"{str(self.amount / self.start * 100)}% of starting amount")
        if self.verbose:
            for i in range(len(self.trades)):
                if i > 0 and self.trades[i][0] == "SELL":
                    print(f"{self.trades[i][0]} at {str(self.trades[i][1])} | {int(((self.trades[i][1] / self.trades[i - 1][1]) * 100) - 100)}%")
                else:
                    print(f"{self.trades[i][0]} at {str(self.trades[i][1])}")

class Pytrade():
    def __init__(self):

        args = self.get_args()

        self.symbol:str = args.symbol
        self.kline_interval:str = args.interval
        self.api_key:str = os.environ["BINANCE_API_KEY"]
        self.api_secret:str = os.environ["BINANCE_API_SECRET"]

        #Binance connection setup
        self.client = Client(self.api_key, self.api_secret)

        print(f"Getting data for {args.symbol} starting {args.startTime}...\n")
        klines = self.client.get_historical_klines(symbol=self.symbol,interval=self.kline_interval, start_str=args.startTime)

        print("Loading strategies...\n")
        strategies = [
            Strategy('MACD', 'CROSS', self.symbol, self.kline_interval, klines),
            Strategy('RSI', '7030', self.symbol, self.kline_interval, klines),
            Strategy('RSI', '8020', self.symbol, self.kline_interval, klines)
        ]

        if args.graph:
            print("Rendering graphs\n")
            for strategy in strategies:
                strategy.plotIndicator()

        print("Backtesting strategies...")
        for strategy in strategies:
            time = strategy.time
            Backtest(100, time[0], time[len(time)-1], strategy, args.verbose)

    def get_args(self):
        parser = argparse.ArgumentParser(description='This is PYTRADE')
        parser.add_argument("--symbol", default="ETHBTC", type=str, help="This is the symbol you wish to trade")
        parser.add_argument("--interval", default="1m", type=str, help="The interval for the trades. Defaults to 1m")
        parser.add_argument('--graph', action='store_true', help="Whether to graph the result")
        parser.add_argument('--verbose', action='store_true', help="Verbose output from backtests")
        parser.add_argument('--startTime', default="1 week ago", help="How long ago to backtest from e.g 1 week ago")
        return parser.parse_args()

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