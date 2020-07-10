class Trade:

    def __init__(self, time, base_coin, trade_coin, action, price, completed:bool=False):
        self.time = time
        self.base_coin:str = base_coin
        self.trade_coin:str = trade_coin
        self.action:str = action
        self.price:str = price
        self.completed:bool = completed
