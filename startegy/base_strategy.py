import backtrader as bt
import pandas as pd
from collections import defaultdict
import csv
from entity.stock_state import StockState


class BaseStrategy(bt.Strategy):
    stock_df = pd.DataFrame(columns=['日期', '股票代码', '持仓', '成本价', '当前价', '盈亏'])
    fund_df = pd.DataFrame(columns=['日期', '现金', '总价值'])
    trade_df = defaultdict(list)
    # 记录股票调仓过程
    stock_state_list = list()

    # 日志函数
    def log(self, txt, dt=None):
        # 以第一个数据data0，即指数作为时间标准
        dt = dt or self.data0.datetime.date(0)
        print("%s，%s" % (dt.isoformat(), txt))

    def notify_order(self, order):
        if order.status in [order.Submitted,order.Accepted]:
            # 订单状态 submited/accepted，无动作
            return
        if order.status in [order.Completed]:
            if order.isbuy():
                if order.executed.psize == order.executed.size:
                    buy_percent = 100.0
                elif order.executed.psize > order.executed.size:
                    buy_percent = ((order.executed.size / (order.executed.psize - order.executed.size))* 100)
                self.log('买单执行，%s，买入价格：%.2f，买入数量：%i，剩余持仓：%i，仓位变动：%0.2f%%' %
                         (order.data._name,order.executed.price, order.executed.size,order.executed.psize,buy_percent))
                stock_state = StockState(order.data._name, get_code_name(order.data._name), 1, order.executed.price,
                                         order.executed.size,'{:.2f}%'.format(buy_percent)).to_dict()
                self.stock_state_list.append(stock_state)

            elif order.issell():
                sell_percent = ((order.executed.size / (abs(order.executed.size) + order.executed.psize)) * 100)
                self.log('卖单执行，%s，卖出价格：%.2f，卖出数量：%i, 剩余持仓：%i，仓位变动：%0.2f%%' %
                         (order.data._name, order.executed.price, order.executed.size, order.executed.psize,sell_percent))
                stock_state = StockState(order.data._name, get_code_name(order.data._name), -1, order.executed.price,
                                        order.executed.size,'{:.2f}%'.format(sell_percent)).to_dict()
                self.stock_state_list.append(stock_state)

        else:
            self.log('订单作废，%s，%s，isbuy=%i，size %i,open price %.2f' % (
            order.data._name, order.getstatusname(), order.isbuy(), order.created.size, order.data.open[0]))
        trade_date = self.data0.datetime.date(0).strftime('%Y-%m-%d')

        self.trade_df[trade_date] = self.stock_state_list

    # 记录交易收益
    def notify_trade(self, trade):
        if trade.isclosed:
            print('毛收益 %0.2f, 扣佣后收益 % 0.2f, 佣金 %.2f, 市值 %.2f, 现金 %.2f' %
                  (trade.pnl, trade.pnlcomm, trade.commission, self.broker.getvalue(), self.broker.getcash()))

    def notify_fund(self, cash, value, fundvalue, shares):
        d = self.datas[0].datetime.date(0)
        for data in self.datas:
            position = self.broker.getposition(data)
            if position.size:
                self.stock_df.loc[len(self.stock_df.index)] = [d, data._name, position.size, position.price,
                                                               position.adjbase,
                                                               position.size * (position.adjbase - position.price)]
        self.fund_df.loc[len(self.fund_df.index)] = [d, cash, value]

def get_code_name(stock_code):
    name = "null"
    with open('D:/Pycharm/Workplace/Trader/stockData/name.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['code'] == stock_code:
                name = row['name']
                break  # 找到匹配项后，停止遍历

    return  name
