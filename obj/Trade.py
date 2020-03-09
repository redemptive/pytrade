class Trade():
    def __init__(self, time, base_coin, trade_coin, action, price, completed=False):
        self.time = time
        self.base_coin = base_coin
        self.trade_coin = trade_coin
        self.action = action
        self.price = price
        self.completed = completed