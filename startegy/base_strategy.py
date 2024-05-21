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

    def log(self, txt, dt=None):
        """
        日志函数
        """
        # 以第一个数据data0，即指数作为时间标准
        dt = dt or self.data0.datetime.date(0)
        print("%s，%s" % (dt.isoformat(), txt))

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # 订单状态 submited/accepted，无动作
            return
        if order.status in [order.Completed]:
            if order.isbuy():
                if order.executed.psize == order.executed.size:
                    buy_percent = 100.0
                elif order.executed.psize > order.executed.size:
                    buy_percent = ((order.executed.size / (order.executed.psize - order.executed.size)) * 100)
                self.log('买单执行，%s，买入价格：%.2f，买入数量：%i，剩余持仓：%i，仓位变动：%0.2f%%' %
                         (order.data._name, order.executed.price, order.executed.size, order.executed.psize,
                          buy_percent))
                stock_state = StockState(order.data._name, get_code_name(order.data._name), 1, order.executed.price,
                                         order.executed.size, '{:.2f}%'.format(buy_percent)).to_dict()
                self.stock_state_list.append(stock_state)

            elif order.issell():
                sell_percent = ((order.executed.size / (abs(order.executed.size) + order.executed.psize)) * 100)
                self.log('卖单执行，%s，卖出价格：%.2f，卖出数量：%i, 剩余持仓：%i，仓位变动：%0.2f%%' %
                         (order.data._name, order.executed.price, order.executed.size, order.executed.psize,
                          sell_percent))
                stock_state = StockState(order.data._name, get_code_name(order.data._name), -1, order.executed.price,
                                         order.executed.size, '{:.2f}%'.format(sell_percent)).to_dict()
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

    def handel_order(self, order_data_list=None, order_list=None, sell_data_list = None):
        """
        处理订单
        order_data_list：需要执行调仓的股票列表
        order_list：记录订单列表
        sell_data_list：不在本次股票池之中，需要进行平仓
        """

        # 先进行平仓处理
        if order_list is None:
            order_list = []
        if sell_data_list is not None and sell_data_list:
            for sell_data in sell_data_list:
                lower_price = sell_data.close[0] * 0.9 + 0.02
                valid_day = sell_data.datetime.datetime(1)
                print('sell 平仓', sell_data._name, self.getposition(sell_data).size)
                o = self.close(data=sell_data, exectype=bt.Order.Limit, price=lower_price, valid=valid_day)
                # 记录订单
                order_list.append(o)

        # 对本次入选股票下单
        # 每只股票买入资金百分比，预留2%的资金以应付佣金和计算误差
        if len(order_data_list) > 0:
            buy_percentage = (1 - 0.02) / len(order_data_list)
        else:
            buy_percentage = 0

        # 得到目标市值
        target_value = buy_percentage * self.broker.getvalue()

        # 为保证先卖后买，股票按照持仓市值从大到小排序
        order_data_list.sort(key=lambda d: self.broker.getvalue([d]), reverse=True)
        self.log('下单, 目标的股票个数 %i, targetvalue %.2f, 当前总市值 %.2f' %
                 (len(order_data_list), target_value, self.broker.getvalue()))
        print(f'{self.data0.datetime.date(0)} 当天入选股票: {"、".join(stock._name for stock in order_data_list)}')

        # 处理股票池中的股票
        if order_data_list is not None and order_data_list:
            for d in order_data_list:
                if len(d.open) > 0 and len(d.close) > 0:
                    # 按照次日开盘价算
                    size = int(
                        abs((self.broker.getvalue([d]) - target_value) / d.open[1] // 100 * 100))
                    # 该股票的下一个实际交易日
                    valid_day = d.datetime.datetime(1)
                    # 如果持仓过多，卖
                    if self.broker.getvalue([d]) > target_value:
                        # 次日跌停价近似值
                        lower_price = d.close[0] * 0.9 + 0.02
                        print(f"{d._name}持仓过多调整")
                        o = self.sell(data=d, size=size, exectype=bt.Order.Limit,
                                      price=lower_price, valid=valid_day)
                    # 持仓过少，买
                    else:
                        # 次日涨停价近似值
                        upper_price = d.close[0] * 1.1 - 0.02
                        print(f"{d._name}持仓过少调整")
                        o = self.buy(data=d, size=size, exectype=bt.Order.Limit,
                                     price=upper_price, valid=valid_day)
                    order_list.append(o)


def get_code_name(stock_code):
    name = "null"
    # with open('/home/c/Downloads/QuantitativeTrading/stockData/stockListName.csv', newline='',
    #           encoding='UTF-8') as csvfile:
    #     reader = csv.DictReader(csvfile)
    #     for row in reader:
    #         if row['code'] == stock_code:
    #             name = row['name']
    #             break  # 找到匹配项后，停止遍历

    return name
