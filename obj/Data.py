# Other imports
import numpy as np
import pandas as pd

from datetime import datetime


class Data:


    @staticmethod
    def process_socket_data(message):
        # This converts the kline from the socket stream to the ohclv data
        # so it is the same as the backtesting historical data returned from API
        # which is what a Strategy accepts
        return [
            message['t'],  # Open time
            message['o'],  # Open
            message['h'],  # High
            message['l'],  # Low
            message['c'],  # Close
            message['v'],  # Volume
            message['T'],  # Close time
            message['q'],  # Quote asset volume
            message['n'],  # Number of trades
            message['V'],  # Taker buy base asset volume
            message['Q'],  # Taker buy quote asset volume
            message['B']  # Ignore
        ]

    @staticmethod
    def process_raw_historic_data(klines):
        data = pd.DataFrame(klines, columns=[
            "open_time",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "close_time",
            "quote_asset_volume",
            "no_trades",
            "taker_buy_base_asset_volume",
            "taker_buy_quote_asset_volume",
            "ignore"
        ])

        # Don't need the following columns
        data = data.drop(columns=[
            "quote_asset_volume",
            "no_trades",
            "taker_buy_base_asset_volume",
            "taker_buy_quote_asset_volume",
            "ignore"
        ])

        # Convert the times to a proper datetime value
        data["open_time"] = data["open_time"].apply(Data.convert_datetime)
        data["close_time"] = data["close_time"].apply(Data.convert_datetime)

        # The prices must be floats
        data["open"] = data["open"].astype("float")
        data["high"] = data["high"].astype("float")
        data["low"] = data["low"].astype("float")
        data["close"] = data["close"].astype("float")
        data["volume"] = data["volume"].astype("float")

        return data

    @staticmethod
    def convert_datetime(value):
        return datetime.fromtimestamp(value / 1000)
