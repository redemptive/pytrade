# Pytrade

A cryptocurrency trading bot written in python.

Create strategies, backtest them and then take those 

## Installation

### Docker Container

By FAR the easiest way to run this is using a container.

I have included a dockerfile for this. Please use a linux host to run it.

- `docker build . -t pytrade`

Without API keys
- `docker run -it pytrade bash`

With API keys
- `docker run --env BINANCE_API_KEY=<your api key> --env BINANCE_API_SECRET=<your api secret> -it pytrade bash`

### Manually

Instructions are for linux. You must have python > 3.5 installed to use this. As well as pip package manager.

#### Installation of the TA Lib Dependancy

- `wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz`
- `tar -xzf ta-lib-0.4.0-src.tar.gz`
- `cd ./ta-lib`
- `./configure --prefix=/usr`
- `make`
- `make install`

#### Installation of pytrade itself

Clone the repository to wherever you would like to keep it and change into the pytrade folder.

- `pip3 install --no-cache-dir -r requirements.txt`

If you have an account then set the following env variables:
- `export BINANCE_API_KEY=<your api key>`
- `export BINANCE_API_SECRET=<your api secret>`


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