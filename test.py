import unittest

from pytrade import Pytrade 

class TestPytrade(unittest.TestCase):

    def test_kline_to_ohclv(self):
        test_kline = {'t': 1583052840000, 'T': 1583052899999, 's': 'ETHBTC', 'i': '1m', 'f': 165732234, 'L': 165732317, 'o': '0.02582100', 'c': '0.02582000', 'h': '0.02582800', 'l': '0.02580400', 'v': '89.60700000', 'n': 84, 'x': True, 'q': '2.31295358', 'V': '48.32900000', 'Q': '1.24753766', 'B': '0'}
        expected_result = [1583052840000, '0.02582100', '0.02582800', '0.02580400', '0.02582000', '89.60700000', 1583052899999, '2.31295358', 84, '48.32900000', '1.24753766', '0']
        result = Pytrade.kline_to_ohlcv(test_kline)
        self.assertEqual(result, expected_result)

if __name__ == '__main__':
    unittest.main()