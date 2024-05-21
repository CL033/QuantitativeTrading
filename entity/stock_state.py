'''
code：股票代码
name：股票名称
state：{1：买入；2：卖出}
price：买卖价格
size：买卖数量
percent：持仓调整比例
'''
class StockState:
    def __init__(self,code,name,state,price,size,percent):
        self.code = code
        self.name = name
        self.state = state
        self.price = price
        self.size = size
        self.percent=percent

    def to_dict(self):
        return {
            'code': self.code,
            'name': self.name,
            'state': self.state,
            'price': self.price,
            'size': self.size,
            'percent':self.percent
        }