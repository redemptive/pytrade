#!/usr/bin/env python3

import unittest
import time
import os

from pytrade import Pytrade
from obj.LiveTrading import LiveTrading

class TestLiveTrading(unittest.TestCase):

    def test_kline_to_ohclv(self):
        test_kline = {'t': 1583052840000, 'T': 1583052899999, 's': 'ETHBTC', 'i': '1m', 'f': 165732234, 'L': 165732317, 'o': '0.02582100', 'c': '0.02582000', 'h': '0.02582800', 'l': '0.02580400', 'v': '89.60700000', 'n': 84, 'x': True, 'q': '2.31295358', 'V': '48.32900000', 'Q': '1.24753766', 'B': '0'}
        expected_result = [1583052840000, '0.02582100', '0.02582800', '0.02580400', '0.02582000', '89.60700000', 1583052899999, '2.31295358', 84, '48.32900000', '1.24753766', '0']
        result = LiveTrading.kline_to_ohlcv(test_kline, False, False)
        self.assertEqual(result, expected_result)

    def test_round_down(self):
        self.assertEqual(LiveTrading.round_down(3.8, 0), 3)
        self.assertEqual(LiveTrading.round_down(2.97, 1), 2.9)

class TestStrategySubcommand(unittest.TestCase):

    def test_default_strategy_creation(self):
        before_length = len(os.listdir('strategies'))
        pytrade = Pytrade(["strategy", "--new", "--name", "test_def"])
        after_length = len(os.listdir('strategies'))
        self.assertEqual(before_length + 1, after_length)
        os.remove("strategies/test_def.json")

    def test_named_strategy_creation(self):
        before_length = len(os.listdir('strategies'))
        pytrade = Pytrade(["strategy", "--new", "--name", "superstrategy"])
        after_length = len(os.listdir('strategies'))
        self.assertEqual(before_length + 1, after_length)
        os.remove("strategies/superstrategy.json")

    def test_custom_strategy(self):
        before_length = len(os.listdir('strategies'))
        pytrade = Pytrade([
            "strategy", "--new", 
            "--name", "customtest",
            "--tradeCoins", "ETH,XRP,XMR",
            "--baseCoin", "BTC",
            "--indicator", "MACD",
            "--strategy", "CROSS",
            "--stopLoss", "3"
        ])
        after_length = len(os.listdir('strategies'))
        self.assertEqual(before_length + 1, after_length)
        os.remove("strategies/customtest.json")

    def test_list_strategies(self):
        pytrade = Pytrade(["strategy", "--list"])

    def test_delete_strategy(self):
        pytrade = Pytrade(["strategy", "--new"])
        before_length = len(os.listdir('strategies'))
        pytrade = Pytrade(["strategy", "--delete", "--name", "test"])
        after_length = len(os.listdir('strategies'))
        self.assertEqual(before_length - 1, after_length)

class TestBacktest(unittest.TestCase):

    def test_all_strategy_backtest(self):
        pytrade = Pytrade(["strategy", "--new", "--name", "test_def_backtest"])
        pytrade = Pytrade(["backtest", "--strategies", "test_def_backtest"])
        os.remove("strategies/test_def_backtest.json")

    def test_multiple_tradecoins_rsi_8020(self):
        pytrade = Pytrade([
            'strategy', '--new',
            '--name', 'test_backtest_rsi_8020_multi',
            '--tradeCoins', 'BTC,ETH,XRP',
            '--baseCoin', 'USDT',
            '--interval', '1d',
            '--indicator', 'RSI',
            '--strategy', '8020',
            '--stopLoss', '3'
        ])
        pytrade = Pytrade(["backtest", "--strategies", "test_backtest_rsi_8020_multi", "--time", "1 month ago"])
        os.remove("strategies/test_backtest_rsi_8020_multi.json")

    def test_single_tradecoin_rsi_7030(self):
        pytrade = Pytrade([
            'strategy', '--new',
            '--name', 'test_backtest_rsi_7030_single',
            '--tradeCoins', 'BTC',
            '--baseCoin', 'USDT',
            '--interval', '1d',
            '--indicator', 'RSI',
            '--strategy', '7020',
            '--stopLoss', '3'
        ])
        pytrade = Pytrade(["backtest", "--strategies", "test_backtest_rsi_7030_single", "--time", "1 month ago"])
        os.remove("strategies/test_backtest_rsi_7030_single.json")

#     def test_multiple_tradecoins_rsi_7030(self):
#         pytrade = Pytrade(False, {
#             'tradeCoins': 'BTC,ETH,XRP',
#             'baseCoin': 'USDT',
#             'interval': '1d',
#             'backtest': True,
#             'time': '6 months ago',
#             'debug': False,
#             'verbose': False,
#             'indicator': 'RSI',
#             'strategy': '7030',
#             'stopLoss': 3
#         })

#     def test_single_tradecoin_macd_cross(self):
#         pytrade = Pytrade(False, {
#             'tradeCoins': 'BTC',
#             'baseCoin': 'USDT',
#             'interval': '1d',
#             'backtest': True,
#             'time': '6 months ago',
#             'debug': False,
#             'verbose': False,
#             'indicator': 'MACD',
#             'strategy': 'CROSS',
#             'stopLoss': 3
#         })

#     def test_multiple_tradecoins_macd_cross(self):
#         pytrade = Pytrade(False, {
#             'tradeCoins': 'BTC,ETH,XRP',
#             'baseCoin': 'USDT',
#             'interval': '1d',
#             'backtest': True,
#             'time': '6 months ago',
#             'debug': False,
#             'verbose': False,
#             'indicator': 'MACD',
#             'strategy': 'CROSS',
#             'stopLoss': 3
#         })

if __name__ == '__main__':
    unittest.main()