from binance.client import Client
from binance.websockets import BinanceSocketManager

class Pytrade():
    def __init__(self):
        self.client = Client()
        self.bm = BinanceSocketManager(self.client)

        self.ticker_socket = self.bm.start_symbol_ticker_socket('ETHBTC', self.process_message)

        self.bm.start()

    def process_message(self, msg):
        print("message type: {}".format(msg['e']))
        print(msg)
        # do something

if __name__ == '__main__':
    pytrade = Pytrade()