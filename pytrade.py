#!/usr/bin/env python3

# Standard libraries
import os
import argparse
import json

# Binance imports
from binance.client import Client

# Custom objects
from obj.Strategy import Strategy
from obj.Backtest import Backtest
from obj.LiveTrading import LiveTrading


class Pytrade():

    def __init__(self, args: list = []):

        self.kline_cache: dict = {}

        # Get credentials from env if they are there and quit if they aren't
        if ("BINANCE_API_KEY" in os.environ):
            self.api_key:str = os.environ["BINANCE_API_KEY"]
            self.api_secret:str = os.environ["BINANCE_API_SECRET"]
            
            print("\nApi keys loaded from env")
            self.client = Client(self.api_key, self.api_secret)   
        else:
            print("No api keys in env. Please enter api creds in BINANCE_API_KEY and BINANCE_API_SECRET env variables")
            quit()

        if args != []: 
            self.args: object = self.get_args(args)
        else: 
            self.args: object = self.get_args()
        
        self.args.func(self.args)

    def manage_strategy(self, args):
        if args.new:
            strategy = {}
            strategy["tradeCoins"] = args.tradeCoins.split(",")
            strategy["baseCoin"] = args.baseCoin
            strategy["interval"] = args.interval
            strategy["indicator_name"] = args.indicator
            strategy["strategy"] = args.strategy
            strategy["stop_loss"] = args.stopLoss

            with open(f"strategies/{args.name}.json", "w") as outfile:
                json.dump(strategy, outfile)

            print(f"New strategy {args.name} created in strategies/{args.name}.json")

        elif args.list:
            for item in os.listdir('strategies'):
                print(item.split(".")[0])
        
        elif args.delete:
            os.remove(f"strategies/{args.name}.json")
            print(f"Strategy {args.name} deleted")

        else:
            print("No option selected")

    def get_args(self, args:list=[]):
        parser = argparse.ArgumentParser(description="This is PYTRADE")

        subparsers = parser.add_subparsers()

        # Strategy command
        parser_strategy = subparsers.add_parser('strategy', help='Manage strategies')
        parser_strategy.add_argument("-n", "--new", action="store_true", help="Create a new strategy")
        parser_strategy.add_argument("-l", "--list", action="store_true", help="List strategies")
        parser_strategy.add_argument("-D", "--delete", action="store_true", help="Delete a strategy")

        parser_strategy.add_argument("-N", "--name", default="test", type=str, help="The name of the strategy")
        parser_strategy.add_argument("-T", "--tradeCoins", default="ETH", type=str, help="This is a comma separated list of the coins you wish to trade. Defaults to ETH")
        parser_strategy.add_argument("-B", "--baseCoin", default="BTC", type=str, help="This is the base coin you will use to pay. Defaults to BTC")
        parser_strategy.add_argument("-i", "--interval", default="1m", type=str, help="The interval for the trades. Defaults to '1m'")
        parser_strategy.add_argument("-I", "--indicator", default="RSI", type=str, help="What indicator to use. Defaults to RSI")
        parser_strategy.add_argument("-S", "--strategy", default="8020", type=str, help="What strategy to use. Defaults to 8020")
        parser_strategy.add_argument("-L", "--stopLoss", default=3, type=int, help="The stop loss percentage. Ie the amount to be losing on a trade before cancelling. Defaults to 3")
        parser_strategy.set_defaults(func=self.manage_strategy)

        # Backtest command
        parser_backtest = subparsers.add_parser('backtest', help='Backtest strategies')
        parser_backtest.add_argument("-t", "--time", default="1 week ago", help="How long ago to backtest from. Defaults to '1 week ago'")
        parser_backtest.add_argument("-s", "--strategies", default="all", type=str, help="A comma separated list of strategies to test. Defaults to 'all' which will test them all")
        parser_backtest.set_defaults(func=self.run_backtest)

        # live command
        parser_live = subparsers.add_parser('live', help='Live trading with strategies')
        parser_live.add_argument("-t", "--time", default="1 day ago", help="How long ago to gather data to 'seed' the live trading. Defaults to '1 day ago'")
        parser_live.add_argument("-s", "--strategy", default="test", help="The name of the strategy to use. Defaults to 'test'")
        parser_live.set_defaults(func=self.run_live_trading)

        # Common args
        parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output from backtests")
        parser.add_argument("-d", "--debug", action="store_true", help="Enable debug output")

        if args == []:
            return parser.parse_args()
        else:
            return parser.parse_args(args)

    def run_live_trading(self, args):
        strategy_data = Pytrade.load_strategy(args.strategy)
        klines = self.get_multi_coin_klines(strategy_data)
        LiveTrading(self.client, Strategy(klines, **strategy_data))

    @staticmethod
    def load_strategy(name):
        with open(f'strategies/{name}.json') as raw:
            print(f"Loading strategy {name}")
            return json.load(raw)

    def get_multi_coin_klines(self, strategy_data): 
        klines = {}

        for coin in strategy_data["tradeCoins"]:
            symbol = f"{coin}{strategy_data['baseCoin']}"
            if strategy_data["interval"] in self.kline_cache.keys() and coin in self.kline_cache[strategy_data["interval"]].keys():
                print(f"Using cached {strategy_data['interval']} interval {symbol} data starting {self.args.time}")
                klines[coin] = self.kline_cache[strategy_data["interval"]][coin]
            else:
                print(f"Getting data for {symbol} starting {self.args.time}...")
                klines[coin] = self.client.get_historical_klines(symbol=symbol, interval=strategy_data["interval"], start_str=self.args.time)
                self.kline_cache[strategy_data["interval"]] = klines
                if self.args.debug:
                    print(klines)

        return klines

    def run_backtest(self, args):

        strategies: list = []

        if args.strategies == "all":
            for item in os.listdir('strategies'):
                strategies.append(item.split(".")[0])
        else:
            strategies = args.strategies.split(",")

        results: dict = {}

        for strategy_name in strategies:
            print(f"\n-------{strategy_name}-------")
            strategy_data = Pytrade.load_strategy(strategy_name)

            klines = self.get_multi_coin_klines(strategy_data)

            print("\nInitialising strategy...\n")
            strategy = Strategy(klines, **strategy_data)

            print("Backtesting strategy...\n")
            backtest = Backtest(100, strategy, self.args.verbose)

            results[strategy_name] = backtest.amount

            print("---------------------")

        if len(results) > 1:
            best_performer = ""
            print()
            for strategy_name in results:
                print(f"Strategy {strategy_name} ended with {results[strategy_name]}")
                if best_performer == "" or results[strategy_name] > results[best_performer]:
                    best_performer = strategy_name

            print(f"\nBest performing strategy was {best_performer} with ending amount of {results[best_performer]}")


if __name__ == "__main__":

    pytrade = Pytrade()
