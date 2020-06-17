## Title

# Pytrade

## Desctiption

A cryptocurrency trading bot written in python

## Usage

### ./pytrade.py
```
usage: pytrade.py [-h] [-v] [-d] {strategy,backtest,live} ...

This is PYTRADE

positional arguments:
  {strategy,backtest,live}
    strategy            Manage strategies
    backtest            Backtest strategies
    live                Live trading with strategies

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         Verbose output from backtests
  -d, --debug           Enable debug output
```

### ./pytrade.py strategy
```
usage: pytrade.py strategy [-h] [-n] [-l] [-D] [-N NAME] [-T TRADECOINS] [-B BASECOIN]
                           [-i INTERVAL] [-I INDICATOR] [-S STRATEGY] [-L STOPLOSS]

optional arguments:
  -h, --help            show this help message and exit
  -n, --new             Create a new strategy
  -l, --list            List strategies
  -D, --delete          Delete a strategy
  -N NAME, --name NAME  The name of the strategy
  -T TRADECOINS, --tradeCoins TRADECOINS
                        This is a comma separated list of the coins you wish to trade. Defaults to
                        ETH
  -B BASECOIN, --baseCoin BASECOIN
                        This is the base coin you will use to pay. Defaults to BTC
  -i INTERVAL, --interval INTERVAL
                        The interval for the trades. Defaults to '1m'
  -I INDICATOR, --indicator INDICATOR
                        What indicator to use. Defaults to RSI
  -S STRATEGY, --strategy STRATEGY
                        What strategy to use. Defaults to 8020
  -L STOPLOSS, --stopLoss STOPLOSS
                        The stop loss percentage. Ie the amount to be losing on a trade before
                        cancelling. Defaults to 3
```

### ./pytrade.py backtest
```
usage: pytrade.py backtest [-h] [-t TIME] [-s STRATEGIES]

optional arguments:
  -h, --help            show this help message and exit
  -t TIME, --time TIME  How long ago to backtest from. Defaults to '1 week ago'
  -s STRATEGIES, --strategies STRATEGIES
                        A comma separated list of strategies to test. Defaults to 'all' which will
                        test them all
```

### ./pytrade.py live
```
usage: pytrade.py live [-h] [-t TIME] [-s STRATEGY]

optional arguments:
  -h, --help            show this help message and exit
  -t TIME, --time TIME  How long ago to gather data to 'seed' the live trading. Defaults to '1 day
                        ago'
  -s STRATEGY, --strategy STRATEGY
                        The name of the strategy to use. Defaults to 'test'
```