"""
code：股票代码
name：名称
high：最高价
low：最低价
close：收盘价
volume：成交量（单位：股）
dv_ratio：市息率
total_share：总股本
total_mv：总市值
"""

class StockInfo:
    def __init__(self, code, name, open, high, low, close, volume, dv_ratio, total_share, total_mv):
        self.code = code
        self.name = name
        self.open = open
        self.high = high
        self.low = low
        self.close = close
        self.volume = volume
        self.dv_ratio = dv_ratio
        self.total_share = total_share
        self.total_mv = total_mv

    def to_dict(self):
        return {
            'code': self.code,
            'name': self.name,
            'open': self.open,
            'high': self.high,
            'low': self.low,
            'close': self.close,
            'volume': self.volume,
            'dv_ratio': self.dv_ratio,
            'total_share': self.total_share,
            'total_mv': self.total_mv,

        }
