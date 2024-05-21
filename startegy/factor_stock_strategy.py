import backtrader as bt
import pandas as pd
from choose_stock.choose_stock import filter_stocks_by_PS_PE_PB
from entity.stock_info import *
import os
from datetime import timedelta
from datetime import datetime

from startegy.base_strategy import BaseStrategy


class FactorStockStrategy(BaseStrategy):
    params = dict(
        rebal_monthday=[2],  # 每月2日重新执行持仓调整
        num_volume=10  # 取成交量前100名
    )

    # choose_stock_df = list()
    csv_files_dir = "D:/Pycharm/Workplace/Trader/stockData/change"

    def __init__(self):
        # print(len(self.data))
        self.end_stock = []  # 最后一天的股票池股票（未到调仓时间）
        self.lastStock = []  # 上次交易股票的列表
        # 记录最后一天的选股结果
        self.choose_stock_df = list()
        self.stocks = self.datas
        # 记录以往的订单，在调整之前全部取消未成交的订单
        self.order_list = []
        # 最后一天时间，即数据的最后一天
        if self.data.datetime.date(0) is not None:
            self.data_end_date = self.data.datetime.date(0)
        # 定时器
        self.add_timer(
            when=bt.Timer.SESSION_START,
            # monthdays=self.p.rebal_monthday ,# 每个月2号触发
            # monthcarry=True, # 如果平衡日不是交易日，则顺延触发
            monthcarry=True,

        )
        # 读取名字列表
        name_df = pd.read_csv('D:/Pycharm/Workplace/Trader/stockData/name.csv', encoding='GBK')
        self.code_name_dict = dict(zip(name_df['code'], name_df['name']))

    def next(self):
        if self.data.datetime.date(0) == self.data_end_date:  # 当前时间是否是最后一天
            # 最后一天入选的股票
            end_stock = filter_stocks_by_PS_PE_PB(self.stocks, self.data.datetime.date(0))
            for d in end_stock:
                csv_file_name = f"{d._name}.csv"
                csv_file_path = os.path.join(self.csv_files_dir, csv_file_name)
                df = pd.read_csv(csv_file_path, encoding='GBK')
                # match_rows = df[df['date'] == self.data.datetime.date(0)]

                df['date'] = pd.to_datetime(df['date'], format='%Y%m%d')

                match_rows = df[df['date'].dt.strftime('%Y%m%d') == self.data_end_date.strftime('%Y%m%d')]

                if not match_rows.empty:
                    code = match_rows['code'].iloc[0]

                    name = self.code_name_dict.get(code, "NULL")
                    open = match_rows['open'].iloc[0]
                    high = match_rows['high'].iloc[0]
                    low = match_rows['low'].iloc[0]
                    close = match_rows['close'].iloc[0]
                    volume = match_rows['volume'].iloc[0]
                    amount = match_rows['amount'].iloc[0]
                    turn = match_rows['turn'].iloc[0]
                    pctChg = match_rows['pct_chg'].iloc[0]
                    peTTM = match_rows['pe'].iloc[0]
                    pbMRQ = match_rows['pb'].iloc[0]
                    psTTM = match_rows['ps'].iloc[0]
                    stock_info = StockInfo(code, name, open, high, low, close, volume, amount, turn, pctChg,
                                           peTTM, pbMRQ, psTTM).to_dict()
                    self.choose_stock_df.append(stock_info)

    def notify_timer(self, timer, when, *args, **kwargs):
        self.stock_state_list = []
        self.rebalance_portfolio()  # 进行持仓调整

    def rebalance_portfolio(self):
        if len(self.data0) > 0:
            self.currDate = self.data0.datetime.date(0)
        else:
            self.log('警告：数据源data0为空，无法获取初始日期')
        if len(self.datas[0]) == self.data0.buflen():
            return
        # 取消以往所下的订单（对于已经成交的不生效）
        for o in self.order_list:
            self.cancel(o)
        # 重置订单列表
        self.order_list = []
        # 最终选取结果
        self.ranks = filter_stocks_by_PS_PE_PB(self.stocks, self.currDate)
        print(str(self.ranks))
        # 按成交量从大到小排序
        self.ranks.sort(key=lambda d: d.volume, reverse=True)
        # 取前 num_volume名
        self.ranks = self.ranks[0:self.p.num_volume]

        # 对于上期入选的股票，本次不入选则先进行平仓
        data_toSell = set(self.lastStock) - set(self.ranks)
        for d in data_toSell:
            lowerprice = d.close[0] * 0.9 + 0.02
            validday = d.datetime.datetime(1)
            print('sell 平仓', d._name, self.getposition(d).size)
            o = self.close(data=d, exectype=bt.Order.Limit, price=lowerprice, valid=validday)
            # 记录订单
            self.order_list.append(o)

        # 本次下单的股票
        # 每只股票买如资金百分比，预留2%的资金以应付佣金和计算误差
        if (len(self.ranks) > 0):
            buypercentage = (1 - 0.02) / len(self.ranks)
        else:
            buypercentage = 0

        # 得到目标市值
        targetvalue = buypercentage * self.broker.getvalue()
        # 为保证先卖后买，股票按照持仓市值从大到小排序
        self.ranks.sort(key=lambda d: self.broker.getvalue([d]), reverse=True)
        self.log('下单, 目标的股票个数 %i, targetvalue %.2f, 当前总市值 %.2f' %
                 (len(self.ranks), targetvalue, self.broker.getvalue()))

        print(f'{self.data0.datetime.date(0)} 当天入选股票: {"、".join(stock._name for stock in self.ranks)}')
        # print('{}当天入选股票{}\n'.format(self.data0.datetime.date(0),str(self.ranks)))
        # 买入股票池中的股票
        for d in self.ranks:
            # print('股票代码',d._name)

            if (len(d.open) > 0 and len(d.close) > 0):
                # 按照次日开盘价算
                size = int(
                    abs((self.broker.getvalue([d]) - targetvalue) / d.open[1] // 100 * 100))
                # 该股票的下一个实际交易日
                validday = d.datetime.datetime(1)
                # 如果持仓过多，卖
                if self.broker.getvalue([d]) > targetvalue:
                    # 次日跌停价近似值
                    lowerprice = d.close[0] * 0.9 + 0.02
                    print(f"{d._name}持仓过多调整")
                    o = self.sell(data=d, size=size, exectype=bt.Order.Limit,
                                  price=lowerprice, valid=validday)
                # 持仓过少，买
                else:
                    # 次日涨停价近似值
                    upperprice = d.close[0] * 1.1 - 0.02
                    print(f"{d._name}持仓过少调整")
                    o = self.buy(data=d, size=size, exectype=bt.Order.Limit,
                                 price=upperprice, valid=validday)
                # print(o)
                # 记录股票订单
                self.order_list.append(o)
        # 跟踪上次买入的股票列表
        self.lastStock = self.ranks
