class Trade:

    def __init__(self, time, base_coin, trade_coin, action, price, comment:str="none", completed:bool=False):
        self.time = time
        self.base_coin:str = base_coin
        self.trade_coin:str = trade_coin
        self.action:str = action
        self.price:str = price
        self.completed:bool = completed
        self.comment:str = comment
    
    @staticmethod
    def new(action, base_coin, trade_coin, df, comment:str="none"):
        return Trade(
            time=df["close_time"],
            base_coin=base_coin,
            trade_coin=trade_coin,
            action=action,
            price=df["close"],
            comment=comment
        )
