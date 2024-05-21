"""
start_cash:初始资金
stamp_duty：印花税率
commission：佣金率
fromdate：开始时间
todate：结束时间
"""

class BaseCerebroData:
    def __init__(self,start_cash,stamp_duty,commission,fromdate,todate):
        self.start_cash = start_cash
        self.stamp_duty = stamp_duty
        self.commission = commission
        self.fromdate = fromdate
        self.todate = todate
