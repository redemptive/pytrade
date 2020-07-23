# Pytrade

A cryptocurrency trading bot written in python. Now with graphs!

Create strategies, backtest them and then take those and trade for real on binance.

Obviously this is just a tool and I take no responsibility for lost cash.

I just let it run in the docker container on my raspberry pi with only small amounts of funds in binance. Be sensible guys.

## Installation

### Docker Container

The easiest way to run this is using a container.

I have included a dockerfile for this. Please use a linux host to run it.
- `docker build . -t pytrade`

Without API keys
- `docker run -it pytrade bash`

With API keys
- `docker run --env BINANCE_API_KEY=<your api key> --env BINANCE_API_SECRET=<your api secret> -it pytrade bash`

### Manually

Instructions are for linux. You must have python > 3.5 installed to use this. As well as pip package manager.
- `pip3 install --no-cache-dir -r requirements.txt`

If you have an account then set the following env variables:
- `export BINANCE_API_KEY=<your api key>`
- `export BINANCE_API_SECRET=<your api secret>`


## Usage

### The Basics

See the section below for full list of commands.

The general workflow when using pytrade is:
- Create a strategy (though some are included)
  - `./pytrade.py strategy --new --name hello` will create a basic strategy called hello. Basic now, not the best or anything.
- Backtest that strategy
  - `./pytrade.py backtest -s hello -t '6 months ago' --graph` will backtest hello strategy against the last 6 months data. Will also graph the results
  - `./pytrade.py backtest -s hello,someStrategy,dude -t '1 year ago'` will backtest hello, someStrategy and dude strategies over the last year and tell you which is the best.
  - `./pytrade.py backtest -t '2 weeks ago'` will backtest all strategies you have over the last two weeks.
- Trade live with your strategy.
  - `./pytrade.py live -s hello -t '2 weeks ago'` will trade live with the hello strategy. Will grab the last two weeks of data so your chosen algorithms can get to work right away.

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
usage: pytrade.py backtest [-h] [-t TIME] [-s STRATEGIES] [-g]

optional arguments:
  -h, --help            show this help message and exit
  -t TIME, --time TIME  How long ago to backtest from. Defaults to '1 week ago'
  -s STRATEGIES, --strategies STRATEGIES
                        A comma separated list of strategies to test. Defaults to 'all' which will
                        test them all
  -g, --graph           Graph the backtest
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

### ./pytrade.py data
```
usage: pytrade.py data [-h] [-s SYMBOL] [-t TIME] [-i INTERVAL] [-g]

optional arguments:
  -h, --help            show this help message and exit
  -s SYMBOL, --symbol SYMBOL
                        The symbol to get the data for. Defaults to 'ETHBTC'
  -t TIME, --time TIME  How far back to get the data. Defaults to '1 month ago'
  -i INTERVAL, --interval INTERVAL
                        What interval to get the recieved data for
  -g, --graph           Graph the recieved data
```