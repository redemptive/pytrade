# Binance imports
from binance.client import Client
from binance.websockets import BinanceSocketManager

import time
from datetime import datetime
import math

from obj.Strategy import Strategy

class LiveTrading:
    def __init__(self, client, trade_coins:list, base_coin, indicator, strategy, kline_interval, stop_loss, verbose, debug):
        self.client = client
        self.trade_coins = trade_coins
        self.base_coin = base_coin
        self.strategy_name = strategy
        self.indicator = indicator
        self.verbose = verbose
        self.debug = debug
        self.kline_interval = kline_interval
        self.stop_loss = stop_loss

        self.precision = {}
        self.klines = {}

        self.message_no = 0

        for coin in trade_coins:
            if self.verbose: print(f"Getting precision for {coin}")
            self.precision[coin] = self.get_precision(coin)
            self.klines[coin] = []

        self.active_order = False

        self.balance = self.client.get_asset_balance(asset=self.base_coin)['free']
        self.starting_balance = self.balance

        print(f"\nStarting trading with the following:")
        print(f"Trade coins: {self.trade_coins}")
        print(f"Starting {self.base_coin}: {self.balance}")
        print(f"Indicator: {self.indicator}")
        print(f"Strategy: {self.strategy_name}")

        self.open_kline_sockets(self.trade_coins)

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
        t = time.localtime()
        current_time = time.strftime("%H:%M:%S", t)
        print(f"\n{current_time} | {message}")

    def process_message(self, msg):
        msg = msg['data']
        if self.verbose: self.print_with_timestamp(f"Recieved kline for {msg['s']}")
        if self.debug: print(msg)

        if (msg['e'] == "kline"): self.process_kline(msg['k'])

    def process_kline(self, kline):
        if kline['x'] == True:
            self.message_no += 1
            self.klines[kline['s'][:len(kline['s']) - len(self.base_coin)]].append(self.kline_to_ohlcv(kline))

            if (self.verbose): self.print_with_timestamp(f"Obtained closed kline and converted to ohlcv. Count for {kline['s']}: {len(self.klines[kline['s'][:len(kline['s']) - len(self.base_coin)]])}")
            if (self.debug): print(self.klines)

            if self.message_no == len(self.trade_coins):
                self.print_with_timestamp("Checking for any actions...")
                self.strategy = Strategy(self.indicator, self.strategy_name, self.trade_coins, self.base_coin, self.kline_interval, self.klines, self.stop_loss)
                if (len(self.strategy.strategy_result) > 0):

                    if self.debug: print(self.strategy.strategy_result)
                    if self.verbose: print(self.klines[-1])
                    # See if the timestamps match on the latest kine and srtategy action
                    # If so, we have a trade to do 
                    if (self.strategy.strategy_result[-1][0] == datetime.fromtimestamp(self.klines[-1][0] / 1000)):
                        if (self.strategy.strategy_result[-1][3] == "BUY"):
                            self.place_buy(self.strategy.strategy_result[-1][4], self.strategy.strategy_result[-1][5])
                        else:
                            self.place_sell(self.strategy.strategy_result[-1][4], self.strategy.strategy_result[-1][5])
                self.message_no = 0

    def place_buy(self, coin, price):
        balance = self.client.get_asset_balance(asset=self.base_coin)
        quantity = self.round_down(float(balance['free']) / float(price), self.precision[coin])
        print(f"Buying {quantity} {coin} at {price}")
        self.active_order = self.client.order_market_buy(
            symbol=f"{coin}{self.base_coin}",
            quantity=quantity
        )
        self.balance = balance

    def place_sell(self, coin, price):
        balance = self.client.get_asset_balance(asset=coin)
        quantity = self.round_down(float(balance['free']), self.precision[coin])
        print(f"\nSelling {quantity} {coin} at {price}")
        self.active_order = self.client.order_market_sell(
            symbol=f"{coin}{self.base_coin}",
            quantity=quantity
        )
        print(f"Result: {self.balance - (quantity * price)}")
        print(f"Percentage: {((self.balance - (quantity * price)) / self.balance) * 100}%")
        print(f"Running percentage: {(self.starting_balance / self.balance) * 100}%")

    def get_precision(self, coin):
        for filt in self.client.get_symbol_info(f"{coin}{self.base_coin}")['filters']:
            if filt['filterType'] == 'LOT_SIZE':
                return int(round(-math.log(float(filt['stepSize']), 10), 0))

    @staticmethod
    def round_down(n, decimals=0):
        multiplier = 10 ** decimals
        return math.floor(n * multiplier) / multiplier

    def kline_to_ohlcv(self, kline):

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

        if self.verbose: print("\nUnpacked closed kline to ohlcv")
        if self.debug: print(ohlcv)

        return ohlcv