"""
code：股票代码
name：名称
high：最高价
low：最低价
close：收盘价
volume：成交量（单位：股）
amount：成交额（单位：元）
turn：换手率
pctChg：涨跌幅（百分比）
peTTM：滚动市盈率
pbMRQ：市净率
psTTM：市销率

"""
class StockInfo:
    def __init__(self,code,name,open,high,low, close,volume,amount,turn,pctChg,peTTM,pbMRQ,psTTM):
        self.code = code
        self.name = name
        self.open = open
        self.high = high
        self.low = low
        self.close = close
        self.volume = volume
        self.amount = amount
        self.turn = turn
        self.pctChg = pctChg
        self.peTTM = peTTM
        self.pbMRQ = pbMRQ
        self.psTTM = psTTM

    def to_dict(self):
        return {
            'code': self.code,
            'name': self.name,
            'open': self.open,
            'high': self.high,
            'low': self.low,
            'close': self.close,
            'volume': self.volume,
            'amount': self.amount,
            'turn': self.turn,
            'pctChg': self.pctChg,
            'peTTM': self.peTTM,
            'pbMRQ': self.pbMRQ,
            'psTTM': self.psTTM,
        }