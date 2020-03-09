## Title

# Pytrade

## Desctiption

A cryptocurrency trading bot written in python

## Usage

```
usage: pytrade.py [-h] [-b | -l] [-T TRADECOINS] [-B BASECOIN] [-i INTERVAL]
                  [-t TIME] [-I INDICATOR] [-S STRATEGY] [-L STOPLOSS] [-v]
                  [-d]

This is PYTRADE

optional arguments:
  -h, --help            show this help message and exit
  -b, --backtest        Backtest some strategies
  -l, --live            Live trading
  -T TRADECOINS, --tradeCoins TRADECOINS
                        This is a comma separated list of the coins you wish
                        to trade. Defaults to ETH
  -B BASECOIN, --baseCoin BASECOIN
                        This is the base coin you will use to pay. Defaults to
                        BTC
  -i INTERVAL, --interval INTERVAL
                        The interval for the trades. Defaults to '1m'
  -t TIME, --time TIME  How long ago to backtest from. Defaults to '1 week
                        ago'
  -I INDICATOR, --indicator INDICATOR
                        What indicator to use. Defaults to RSI
  -S STRATEGY, --strategy STRATEGY
                        What strategy to use. Defaults to 8020
  -L STOPLOSS, --stopLoss STOPLOSS
                        The stop loss percentage. Ie the amount to be losing
                        on a trade before cancelling. Defaults to 5
  -v, --verbose         Verbose output from backtests
  -d, --debug           Enable debug output
```

