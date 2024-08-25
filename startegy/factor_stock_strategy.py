import backtrader as bt
import pandas as pd
from entity.stock_info import *
import util.constant as CONSTANT
import os

from startegy.base_strategy import BaseStrategy

# 股票数据路径
csv_files_dir = CONSTANT.DEFAULT_DIR + "/Factor/FactoryData"


class FactorStockStrategy(BaseStrategy):
    params = dict(
        rebal_monthday=[2],  # 每月2日重新执行持仓调整
        num_volume=10  # 取成交量前100名
    )

    def __init__(self):
        super().__init__()
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
        name_df = pd.read_csv(CONSTANT.DEFAULT_DIR + '/stockListName.csv', encoding='GBK')
        self.code_name_dict = dict(zip(name_df['code'], name_df['name']))

    def next(self):
        if self.data.datetime.date(0) == self.data_end_date:  # 当前时间是否是最后一天
            # 最后一天入选的股票
            end_stock = filter_stocks_by_PS_PE_PB(self.stocks, self.data.datetime.date(0))

            for d in end_stock:
                csv_file_name = f"{d._name}.csv"
                csv_file_path = os.path.join(csv_files_dir, csv_file_name)
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
        # 按成交量从大到小排序
        self.ranks.sort(key=lambda d: d.volume, reverse=True)
        # 取前 num_volume名
        self.ranks = self.ranks[0:self.p.num_volume]

        # 对于上期入选的股票，本次不入选则先进行平仓
        sell_list = set(self.lastStock) - set(self.ranks)
        self.handel_order(self.ranks, self.order_list, sell_list)
        # 跟踪上次买入的股票列表
        self.lastStock = self.ranks


# 三低策略筛选方法
def filter_stocks_by_PS_PE_PB(stockDatas, currentDate):
    selected_stocks = [
        d for d in stockDatas
        if len(d) > 0  # 至少要有一根实际bar
           and d.datetime.date(0) == currentDate
           and 0 < d.peTTM < 20
           # and d.pbMRQ >= 0
           and d.close < 10
        # and d.psTTM >= 0
        # and d.psTTM <= 1
    ]
    return selected_stocks
