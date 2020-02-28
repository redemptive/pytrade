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

        args = self.get_args()

        self.symbol:str = args.symbol
        self.kline_interval:str = args.interval
        self.api_key:str = os.environ["BINANCE_API_KEY"]
        self.api_secret:str = os.environ["BINANCE_API_SECRET"]

        #Binance connection setup
        self.client = Client(self.api_key, self.api_secret)

        if args.backtest:
            print(f"Getting data for {args.symbol} starting {args.startTime}...\n")
            klines = self.client.get_historical_klines(symbol=self.symbol,interval=self.kline_interval, start_str=args.startTime)

            if args.debug:
                print(klines)

            print("Loading strategies...\n")
            strategies = [
                Strategy("MACD", "CROSS", self.symbol, self.kline_interval, klines),
                Strategy("RSI", "7030", self.symbol, self.kline_interval, klines),
                Strategy("RSI", "8020", self.symbol, self.kline_interval, klines)
            ]

            if args.graph:
                print("Rendering graphs\n")
                for strategy in strategies:
                    strategy.plotIndicator()

            print("Backtesting strategies...")
            for strategy in strategies:
                Backtest(100, strategy.time[0], strategy.time[len(strategy.time)-1], strategy, args.verbose)
        elif args.live:
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
        self.bm = BinanceSocketManager(self.client)
        self.kline_socket = self.bm.start_kline_socket(symbol, self.process_message)
        self.bm.start()

    def open_ticker_socket(self, symbol:str):
        self.bm = BinanceSocketManager(self.client)
        self.ticker_socket = self.bm.start_symbol_ticker_socket(symbol, self.process_message)
        self.bm.start()

    def process_message(self, msg):
        print("message type: {}".format(msg["e"]))
        print(msg)

    def getBalances(self):
        prices = self.client.get_withdraw_history()
        return prices

if __name__ == "__main__":
    pytrade = Pytrade()