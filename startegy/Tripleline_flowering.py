
import backtrader as bt
import matplotlib.pyplot as plt
import akshare as ak
import pandas as pd
import numpy as np
import backtrader.indicators as btind
#
plt.rcParams["font.sans-serif"]=["SimHei"] #设置画图时的中文显示
plt.rcParams["axes.unicode_minus"]=False #设置画图时的负号显示
#设置显示的最大列、宽等参数，消掉打印不完全中间的省略号
pd.set_option('display.width', 1000)#加了这一行那表格的一行就不会分段出现了
#显示所有列
pd.set_option('display.max_columns', None)
#显示所有行
pd.set_option('display.max_rows', None)
# 获取数据
def getData(symbol,start_date,end_date):
    stock_pinan = ak.stock_zh_a_hist(symbol=symbol,period="daily",start_date=start_date,end_date=end_date,adjust='qfq')
    stock_pinan = stock_pinan[['日期', '开盘', '收盘', '最高', '最低', '成交量']]
    # print(stock_pinan)
    stock_pinan.columns = ["date","open", "close", "high", "low", "volume"]
    stock_pinan['openinterest'] = 0
    stock_pinan["date"]= pd.to_datetime(stock_pinan['date'])
    # 设置索引
    stock_pinan.set_index("date",inplace=True)
    return stock_pinan

class MyStrategy(bt.Strategy):
    params = dict(
        short_period = 5,
        middle_period = 40,
        long_period = 70,
        printlog=False)
    def log(self,txt,dt=None, doprint =False):
        if self.params.printlog or doprint:
            dt = dt or self.data.datetime.date(0)
            print(f'{dt.isoformat()},{txt}')
    def __init__(self):
        self.order = None
        self.close = self.datas[0].close
        self.s_ma = bt.ind.SMA(period=int(self.p.short_period))
        self.m_ma = bt.ind.SMA(period=int(self.p.middle_period))
        self.l_ma = bt.ind.SMA(period=int(self.p.long_period))
        # 捕获做多信号
        # 短期均线在中期均线上方，且中期均取也在长期均线上方，三线多头排列，取值为1；反之，取值为0
        self.signal1 = bt.And(self.m_ma > self.l_ma, self.s_ma > self.m_ma)
        # 做多信号，求上面 self.signal1 的环比增量，可以判断得到第一次同时满足上述条件的时间，第一次满足条件为1，其余条件为0
        self.long_signal = bt.If((self.signal1 - self.signal1(-1)) > 0, 1, 0)
        # 做多平仓信号，短期均线下穿长期均线时，取值为1；反之取值为0
        self.close_long_signal = bt.ind.CrossDown(self.s_ma, self.m_ma)
        # 捕获做空信号和平仓信号，与做多相反
        self.signal2 = bt.And(self.m_ma < self.l_ma, self.s_ma < self.m_ma)
        self.short_signal = bt.If((self.signal2 - self.signal2(-1)) > 0, 1, 0)
        self.close_short_signal = bt.ind.CrossUp(self.s_ma, self.m_ma)



    def next(self):
            # 如果已经持仓
            if self.position.size > 0:
                if(self.close_long_signal==1):
                    self.order = self.sell(size=abs(self.position.size))
            elif self.position.size<0:
                if self.close_short_signal == 1:
                    self.order = self.buy(size=abs(self.position.size))
            else:  # 如果没有持仓，等待入场时机
                # 入场: 出现做多信号，做多，开四分之一仓位
                if self.long_signal == 1:
                    # 实现买入逻辑，这里我们使用三线开花信号来确定买入时机
                    self.buy_unit = int(self.broker.getvalue() / self.close[0] / 4)  # 根据你的逻辑调整买入单位的大小
                    self.order = self.buy(size=self.buy_unit)
                elif self.short_signal == 1:
                    # 实现卖出逻辑，这里我们使用三线开花信号来确定卖出时机
                    self.sell_unit = int(self.broker.getvalue() / self.close[0] / 4)  # 根据你的逻辑调整卖出单位的大小
                    self.order = self.sell(size=self.sell_unit)

    def notify_order(self, order):
        order_status = ['Created','Submitted','Accepted','Partial',
                        'Completed','Canceled','Expired','Margin','Rejected']
        # 未被处理的订单
        if order.status in [order.Submitted,order.Accepted]:
            print('ref：%.0f,name：%s,Order：%s'%(order.ref,order.data._name,order_status[order.status]))
            return

        #已经辈被处理的订单
        if order.status in [order.Partial,order.Completed]:
            if order.isbuy():
                print(
                    'BUY EXECUTED status：%s,ref：%.0f,name：%s, Size：%.2f, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (
                        order_status[order.status],
                        order.ref, # 订单编号
                        order.data._name, # 股票名称
                        order.executed.size, # 成交量
                        order.executed.price, # 成交价
                        order.executed.value, # 成交额
                        order.executed.comm,  # 佣金
                    ))
            else:
                print(
                    'SELL EXECUTED status：%s,ref：%.0f,name：%s, Size：%.2f, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (
                        order_status[order.status],
                        order.ref,  # 订单编号
                        order.data._name,  # 股票名称
                        order.executed.size,  # 成交量
                        order.executed.price,  # 成交价
                        order.executed.value,  # 成交额
                        order.executed.comm,  # 佣金
                    ))
        elif order.status in [order.Canceled, order.Margin, order.Rejected, order.Expired]:
            # 订单未完成
            print('ref:%.0f, name: %s, status: %s' % (
                order.ref, order.data._name, order_status[order.status]))
        self.order = None

if __name__ =='__main__':
    # 创建大脑
    cerebro = bt.Cerebro();
    cerebro.broker.setcash(25000.00)
    # 获取数据
    stock = getData('600519','20200128','20230128')
    data =  bt.feeds.PandasData(dataname = stock)
    # 添加数据
    cerebro.adddata(data)
    #设置策略
    cerebro.addstrategy(MyStrategy)
    # # 设置交易手续费
    cerebro.broker.setcommission(commission=0.0005)
    cerebro.addanalyzer(bt.analyzers.AnnualReturn, _name='AnnualReturn')
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='_SharpeRatio')
    print('初始资金：%.2f' % cerebro.broker.getvalue())
    result = cerebro.run()
    print('最终资金：%.2f' % cerebro.broker.getvalue())
    # cerebro.addanalyzer(bt.analyzers.SharpeRatio,_name = 'SharpeRatio')
    # cerebro.addanalyzer(bt.analyzers.DrawDown,_name = 'DW')
    # result = cerebro.run()
    start = result[0]
    print('年收益率：', start.analyzers.AnnualReturn.get_analysis())
    print('夏普比率：', start.analyzers._SharpeRatio.get_analysis()['sharperatio'])
    # print('回撤指标：', start.analyzers.DW.get_analysis())
    # cerebro.plot(style='candlestick', barup = '#ff9896', bardown='#98df8a',volup='#ff9896', voldown='#98df8a')
    # cerebro.plot(iplot=False, style='candlestick', barup='red', bardown='green', volume=True, volup='red', voldown='green')
    cerebro.plot()
