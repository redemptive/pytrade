# Binance imports
from binance.client import Client
from binance.websockets import BinanceSocketManager

import time
from datetime import datetime
import math

from obj.Strategy import Strategy

class LiveTrading:
    def __init__(self, client:object, trade_coins:list, base_coin:str, 
                indicator:str, strategy:str, kline_interval:str, 
                stop_loss:int, verbose:bool, debug:bool):

        self.client:object = client
        self.trade_coins:list = trade_coins
        self.base_coin:str = base_coin
        self.strategy_name:str = strategy
        self.indicator:str = indicator
        self.verbose:bool = verbose
        self.debug:bool = debug
        self.kline_interval:str = kline_interval
        self.stop_loss:int = stop_loss

        self.precision:dict = {}
        self.klines:dict = {}

        self.message_no = 0

        for coin in trade_coins:
            if self.verbose: print(f"Getting precision for {coin}")
            self.precision[coin] = self.get_precision(coin)
            self.klines[coin] = []

        self.active_order = False
        self.open_trade = False

        self.balance = self.get_balance(self.base_coin)
        self.starting_balance = self.balance

        print(f"\nStarting trading with the following:")
        print(f"Trade coins: {self.trade_coins}")
        print(f"Starting {self.base_coin}: {self.balance}")
        print(f"Indicator: {self.indicator}")
        print(f"Strategy: {self.strategy_name}")

        self.open_kline_sockets(self.trade_coins)

    def get_balance(self, coin):
        return float(self.client.get_asset_balance(asset=coin)["free"])

    def open_kline_sockets(self, coins:list):
        print(f"\nOpening kline socket for {coins}")
        self.bm = BinanceSocketManager(self.client)

        sockets = []

        for coin in coins:
            sockets.append(f"{coin.lower()}{self.base_coin.lower()}@kline_{self.kline_interval}")

        self.kline_socket = self.bm.start_multiplex_socket(sockets, self.process_message)
        self.bm.start()
    
    @staticmethod
    def print_with_timestamp(message):
        print(f"\n{time.strftime('%H:%M:%S', time.localtime())} | {message}")

    def process_message(self, msg):
        msg = msg["data"]
        if self.verbose: self.print_with_timestamp(f"Recieved kline for {msg['s']}")
        if self.debug: print(msg)

        if (msg['e'] == "kline"): self.process_kline(msg['k'])

    def process_kline(self, kline):
        if kline['x'] == True:
            self.message_no += 1
            self.klines[kline['s'][:len(kline['s']) - len(self.base_coin)]].append(self.kline_to_ohlcv(kline, self.verbose, self.debug))

            if (self.verbose): self.print_with_timestamp(f"Obtained closed kline and converted to ohlcv. Count for {kline['s']}: {len(self.klines[kline['s'][:len(kline['s']) - len(self.base_coin)]])}")
            if (self.debug): print(self.klines)

            if self.message_no == len(self.trade_coins):
                self.message_no = 0
                self.print_with_timestamp("Checking for any actions...")
                self.strategy = Strategy(self.indicator, self.strategy_name, self.trade_coins, self.base_coin, self.kline_interval, self.klines, self.stop_loss)
                if (len(self.strategy.strategy_result) > 0):

                    if self.debug: print(self.strategy.strategy_result)
                    if self.verbose: print(self.klines[-1])
                    
                    # See if the timestamps match on the latest kine and strategy action
                    # If so, we have a trade to do
                    latest_result = self.strategy.strategy_result[-1]
                    if ((not self.active_order) and (latest_result[3] == "BUY")):
                        self.active_order = True
                        self.place_buy(latest_result[5], latest_result[4])

                    elif ((self.active_order) and (latest_result[3] == "SELL")):
                        self.active_order = False
                        self.place_sell(latest_result[5], latest_result[4])

    def place_buy(self, coin, price):
        self.balance = self.get_balance(self.base_coin)
        quantity = self.round_down(self.balance / float(price), self.precision[coin])
        print(f"Buying {quantity} {coin} at {price}")
        self.active_order = self.client.order_market_buy(
            symbol=f"{coin}{self.base_coin}",
            quantity=quantity
        )

    def place_sell(self, coin, price):
        balance = self.client.get_asset_balance(asset=coin)
        quantity = self.round_down(balance, self.precision[coin])
        print(f"\nSelling {quantity} {coin} at {price}")
        self.active_order = self.client.order_market_sell(
            symbol=f"{coin}{self.base_coin}",
            quantity=quantity
        )
        self.balance = self.client.get_balance(self.base_coin)
        print(f"Result: {self.balance - (quantity * price)}")
        print(f"Percentage: {((self.balance - (quantity * price)) / self.balance) * 100}%")
        print(f"Running percentage: {(self.starting_balance / self.balance) * 100}%")

    def get_precision(self, coin):
        for filt in self.client.get_symbol_info(f"{coin}{self.base_coin}")['filters']:
            if filt['filterType'] == 'LOT_SIZE':
                return int(round(-math.log(float(filt['stepSize']), 10), 0))

    @staticmethod
    def round_down(n, decimals=0):
        return math.floor(n * (10 ** decimals)) / 10 ** decimals

    @staticmethod
    def kline_to_ohlcv(kline, verbose, debug):

        # This converts the kline from the socket stream to the ohclv data
        # so it is the same as the backtesting historical data returned from API
        ohlcv = [
            # Open time
            kline['t'],
            # Open
            kline['o'],
            # High
            kline['h'],
            # Low
            kline['l'],
            # Close
            kline['c'],
            # Volume
            kline['v'],
            # Close time
            kline['T'],
            # Quote asset volume
            kline['q'],
            # Number of trades
            kline['n'],
            # Taker buy base asset volume
            kline['V'],
            # Taker buy quote asset volume
            kline['Q'],
            # Ignore
            kline['B']
        ]

        if verbose: print("\nUnpacked closed kline to ohlcv")
        if debug: print(ohlcv)

        return ohlcv