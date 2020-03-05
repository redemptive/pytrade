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
import time

from obj.Strategy import Strategy
from obj.Backtest import Backtest
from obj.LiveTrading import LiveTrading

class Pytrade():
    def __init__(self):

        self.args:object = self.get_args()

        #self.symbol:str = f"{self.args.tradeCoins[0]}{self.args.baseCoin}"
        self.kline_interval:str = self.args.interval

        self.tradeCoins = self.args.tradeCoins.split(",")

        # Get credentials from env if they are there
        # And set up the binance client with or without creds
        if ("BINANCE_API_KEY" in os.environ):
            self.api_key:str = os.environ["BINANCE_API_KEY"]
            self.api_secret:str = os.environ["BINANCE_API_SECRET"]
            
            print("\nApi keys loaded from env")
            self.client = Client(self.api_key, self.api_secret)   
        else:
            print("No api keys in env. Live trading will run in test mode")
            self.client = Client()

        self.klines = []

        if self.args.backtest: self.run_backtest()
        elif self.args.live: self.run_live_trading()
        else: print("Please select --backtest (-b) or --live (-l) mode")

    def get_args(self):
        parser = argparse.ArgumentParser(description="This is PYTRADE")

        # Backtest and live are mutually exclusive, you can't use both at once
        group = parser.add_mutually_exclusive_group()
        group.add_argument("-b", "--backtest", action="store_true", help="Backtest some strategies")
        group.add_argument("-l", "--live", action="store_true", help="Live trading")

        # Other arguments
        parser.add_argument("-T", "--tradeCoins", default="ETH", type=str, help="This is a comma separated list of the coins you wish to trade. Defaults to ETH")
        parser.add_argument("-B", "--baseCoin", default="BTC", type=str, help="This is the base coin you will use to pay. Defaults to BTC")
        parser.add_argument("-i", "--interval", default="1m", type=str, help="The interval for the trades. Defaults to '1m'")
        parser.add_argument("-g", "--graph", action="store_true", help="Whether to graph the result")
        parser.add_argument("-t", "--time", default="1 week ago", help="How long ago to backtest from. Defaults to '1 week ago'")
        parser.add_argument("-I", "--indicator", default="RSI", type=str, help="What indicator to use. Defaults to RSI")
        parser.add_argument("-S", "--strategy", default="8020", type=str, help="What strategy to use. Defaults to 8020")
        parser.add_argument("-L", "--stopLoss", default=3, type=int, help="The stop loss percentage. Ie the amount to be losing on a trade before cancelling. Defaults to 5")

        # Common args
        parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output from backtests")
        parser.add_argument("-d", "--debug", action="store_true", help="Enable debug output")
        return parser.parse_args()

    def run_live_trading(self):
        LiveTrading(self.client, self.tradeCoins, self.args.baseCoin, self.args.indicator, self.args.strategy, self.args.interval, self.args.stopLoss, self.args.verbose, self.args.debug)

    def run_backtest(self):
        
        klines = {}

        for coin in self.tradeCoins:
            symbol = f"{coin}{self.args.baseCoin}"
            fees = self.client.get_trade_fee(symbol=symbol)
            print(f"\nFee for {symbol} is {fees['tradeFee'][0]['maker']}")
            print(f"Getting data for {symbol} starting {self.args.time}...\n")
            klines[coin] = self.client.get_historical_klines(symbol=symbol,interval=self.kline_interval, start_str=self.args.time)

            if self.args.debug:
                print(klines)

        print("Loading strategy...\n")
        strategy = Strategy(self.args.indicator, self.args.strategy, self.tradeCoins, self.args.baseCoin, self.kline_interval, klines, self.args.stopLoss)

        if self.args.graph:
            print("Rendering graphs\n")
            strategy.plot_indicator()

        print("Backtesting strategy...")
        Backtest(100, strategy.time[self.tradeCoins[-1]][0], strategy.time[self.tradeCoins[-1]][-1], strategy, self.args.verbose)

if __name__ == "__main__":
    pytrade = Pytrade()