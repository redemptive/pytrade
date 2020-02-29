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

from obj.Strategy import Strategy
from obj.Backtest import Backtest

class Pytrade():
    def __init__(self):

        self.args:object = self.get_args()

        self.symbol:str = self.args.symbol
        self.kline_interval:str = self.args.interval
        self.api_key:str = os.environ["BINANCE_API_KEY"] or ""
        self.api_secret:str = os.environ["BINANCE_API_SECRET"] or ""

        self.klines = []

        #Binance connection setup
        if (self.api_key != "") and (self.api_secret != ""):
            print("\nApi keys loaded from env")
            self.client = Client(self.api_key, self.api_secret)
        else:
            print("No api keys in env. Live trading will run in test mode")
            self.client = Client()

        if self.args.backtest:
            print(f"Getting data for {self.args.symbol} starting {self.args.startTime}...\n")
            klines = self.client.get_historical_klines(symbol=self.symbol,interval=self.kline_interval, start_str=self.args.startTime)

            if self.args.debug:
                print(klines)

            print("Loading strategies...\n")
            strategies = [
                Strategy("MACD", "CROSS", self.symbol, self.kline_interval, klines),
                Strategy("RSI", "7030", self.symbol, self.kline_interval, klines),
                Strategy("RSI", "8020", self.symbol, self.kline_interval, klines)
            ]

            if self.args.graph:
                print("Rendering graphs\n")
                for strategy in strategies:
                    strategy.plot_indicator()

            print("Backtesting strategies...")
            for strategy in strategies:
                Backtest(100, strategy.time[0], strategy.time[len(strategy.time)-1], strategy, self.args.verbose)
        elif self.args.live:
            self.open_kline_socket(self.symbol)
        else:
            print("Please select --backtest (-b) or --live (-l) mode")

    def get_args(self):
        parser = argparse.ArgumentParser(description="This is PYTRADE")
        group = parser.add_mutually_exclusive_group()
        group.add_argument("-b", "--backtest", action="store_true", help="Backtest some strategies")
        group.add_argument("-l", "--live", action="store_true", help="Live trading")
        parser.add_argument("-s", "--symbol", default="ETHBTC", type=str, help="This is the symbol you wish to trade")
        parser.add_argument("-i", "--interval", default="1m", type=str, help="The interval for the trades. Defaults to 1m")
        parser.add_argument("-g", "--graph", action="store_true", help="Whether to graph the result")
        parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output from backtests")
        parser.add_argument("-S", "--startTime", default="1 week ago", help="How long ago to backtest from e.g 1 week ago")
        parser.add_argument("-d", "--debug", action="store_true", help="Enable debug output")
        return parser.parse_args()

    def open_kline_socket(self, symbol:str):
        print(f"\nOpening kline socket for {self.symbol}")
        self.bm = BinanceSocketManager(self.client)
        self.kline_socket = self.bm.start_kline_socket(symbol, self.process_message)
        self.bm.start()

    def open_ticker_socket(self, symbol:str):
        self.bm = BinanceSocketManager(self.client)
        self.ticker_socket = self.bm.start_symbol_ticker_socket(symbol, self.process_message)
        self.bm.start()

    def process_message(self, msg):
        print(f"\nRecieved message type: {msg['e']}")
        if self.args.debug:
            print(msg)

        if (msg['e'] == "kline"):
            self.process_kline(msg['k'])

    def process_kline(self, kline):
        if kline['x'] == True:
            self.klines.append(self.kline_to_ohlcv(kline))

            print(f"Obtained closed kline and converted to ohlcv. Count {len(self.klines)}")
            if (self.args.debug):
                print(self.klines)

    def kline_to_ohlcv(self, kline):
        # print(len(self.klines))
        # if (len(self.klines) < 1):
        #     open_time = kline['t']
        # else:
        #     print(self.klines[-1])
        #     open_time = self.klines[-1][0]

        ohlcv = [
            kline['t'],
            kline['o'],
            kline['h'],
            kline['l'],
            kline['c'],
            kline['v'],
            kline['T'],
            kline['q'],
            kline['n'],
            kline['V'],
            kline['Q'],
            kline['B']
        ]

        if self.args.verbose:
            print("\nUnpacked closed kline to ohlcv:")
            print(ohlcv)

        return ohlcv

    def get_balances(self):
        prices = self.client.get_withdraw_history()
        return prices

if __name__ == "__main__":
    pytrade = Pytrade()