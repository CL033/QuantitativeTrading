import backtrader as bt
import pandas as pd
from choose_stock.choose_stock import michael_sivy_filter
from entity.stock_info import *
import os
from startegy.base_strategy import BaseStrategy
from datetime import datetime, timedelta

# 对应的日期调整
CONSTANT_ADJUST_DATE = {
    4: (3, 31),
    7: (6, 30),
    10: (9, 30),
    1: (12, 31)
}


def is_trading_day(date):
    """
    判断是否在交易日
    """
    # 判断是否在10月1号到7号之间
    if date.month == 10 and 1 <= date.day <= 7:
        return False
    # 判断是否是周一到周五
    return date.weekday() < 5


def get_adjusted_date(current_date):
    """
    对时间进行调整，比如9月30是休息日，则调仓会延续要10月份进行，那么获取的年报数据仍然是9月30的年报
    """
    current_year = current_date.year
    adjust_month_day = CONSTANT_ADJUST_DATE.get(current_date.month)

    if adjust_month_day:
        adjust_month, adjust_day = adjust_month_day
        if current_date.month == 1:
            current_year -= 1
        adjusted_date = datetime(current_year, adjust_month, adjust_day)
    else:
        adjusted_date = current_date
    return adjusted_date


class QuarterEndChecker(object):
    """
    自定义定时器，每个季度触发，如果是休息日则继续往后延续直到第一个工作日
    """
    def __init__(self, datafeed):
        self.comparison_dates = [(3, 31), (6, 30), (9, 30), (12, 31)]
        self.datafeed = datafeed
        self.current_date = (-1, -1)
        print(str(self.datafeed))

    def __call__(self, d):
        for i, (month, day) in enumerate(self.comparison_dates):
            baseline = datetime(d.year, month, day)
            if baseline.weekday() >= 5:
                adjustment = 2 if baseline.weekday() == 5 else 1
                adjusted_date = baseline + timedelta(days=adjustment)
                self.comparison_dates[i] = (adjusted_date.month, adjusted_date.day)

            while not is_trading_day(baseline):
                baseline += timedelta(days=1)
            self.comparison_dates[i] = (baseline.month, baseline.day)
        self.current_date = (d.month, d.day)
        # print(str(self.comparison_dates))
        return any((month, day) == self.current_date for month, day in self.comparison_dates)


class MichaelSivyStrategy(BaseStrategy):
    params = dict(
        num_volume=10  # 取成交量前100名
    )

    # choose_stock_df = list()
    # csv_files_dir = "D:/Pycharm/Data/overview_all_data4/test1"

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
        self.quarter_end_checker = QuarterEndChecker(self.data)
        # 定时器
        self.add_timer(
            when=bt.Timer.SESSION_START,
            # monthcarry=True,
            allow=self.quarter_end_checker
            # monthdays=self.p.rebal_monthday ,# 每个月2号触发
            # monthcarry=True, # 如果平衡日不是交易日，则顺延触发
        )
        # 读取名字列表
        name_df = pd.read_csv('/home/c/Downloads/QuantitativeTrading/stockData/stockListName.csv', encoding='GBK')
        self.code_name_dict = dict(zip(name_df['code'], name_df['name']))

    def next(self):
        pass
        # self.counter = 0  # 重置计数
        # self.next_operation_day = self.next_operation_day.replace(hour=0, minute=0, second=0, microsecond=0)

        # if self.data.datetime.date(0) == self.data_end_date:  # 当前时间是否是最后一天
        #     # 最后一天入选的股票
        #     end_stock = michael_sivy_filter(self.stocks, self.data.datetime.date(0))
        #     for d in end_stock:
        #         csv_file_name = f"{d._name}.csv"
        #         csv_file_path = os.path.join(self.csv_files_dir, csv_file_name)
        #         df = pd.read_csv(csv_file_path, encoding='GBK')
        #         # match_rows = df[df['date'] == self.data.datetime.date(0)]
        #
        #         df['date'] = pd.to_datetime(df['date'], format='%Y%m%d')
        #
        #         match_rows = df[df['date'].dt.strftime('%Y%m%d') == self.data_end_date.strftime('%Y%m%d')]
        #
        #         if not match_rows.empty:
        #             code = match_rows['code'].iloc[0]
        #
        #             name = self.code_name_dict.get(code, "NULL")
        #             open = match_rows['open'].iloc[0]
        #             high = match_rows['high'].iloc[0]
        #             low = match_rows['low'].iloc[0]
        #             close = match_rows['close'].iloc[0]
        #             volume = match_rows['volume'].iloc[0]
        #             amount = match_rows['amount'].iloc[0]
        #             turn = match_rows['turn'].iloc[0]
        #             pctChg = match_rows['pct_chg'].iloc[0]
        #             peTTM = match_rows['pe'].iloc[0]
        #             pbMRQ = match_rows['pb'].iloc[0]
        #             psTTM = match_rows['ps'].iloc[0]
        #             stock_info = StockInfo(code, name, open, high, low, close, volume, amount, turn, pctChg,
        #                                    peTTM, pbMRQ, psTTM).to_dict()
        #             self.choose_stock_df.append(stock_info)

    def notify_timer(self, timer, when, *args, **kwargs):
        self.stock_state_list = []
        self.rebalance_portfolio()  # 进行持仓调整

    # 进行调仓
    def rebalance_portfolio(self):
        print(self.data0.datetime.date(0))
        current_date = self.data0.datetime.date(0)
        # 获取当前年份
        current_year = current_date.year
        adjustment_dates = {
            4: (current_year, 3, 31),
            7: (current_year, 6, 30),
            10: (current_year, 9, 30),
            1: (current_year - 1, 12, 31)
        }
        adjusted_date = datetime(
            *adjustment_dates.get(current_date.month, (current_year, current_date.month, current_date.day)))

        filename = adjusted_date.strftime('%Y%m%d')  # 格式化日期为 YYYYMMDD
        csv_folder_path = '/home/c/Downloads/QuantitativeTrading/stockData/new'
        filename = filename + '.csv'
        csv_file_path = os.path.join(csv_folder_path, filename)

        # 检查文件是否存在再尝试读取
        if os.path.exists(csv_file_path):
            df = pd.read_csv(csv_file_path).fillna(0)
            print(f"成功读取了日期为 {filename} 的数据")
        else:
            print(f"未找到日期为 {filename} 的CSV文件")

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
        self.ranks = michael_sivy_filter(df)
        print(f"code：{len(self.ranks)}")
        # print(str(self.ranks))
        self.ranks = self.filter_stocks(self.ranks)
        # print(str(self.ranks))

        # 按成交量从大到小排序
        self.ranks.sort(key=lambda d: d.volume, reverse=True)
        # 取前 num_volume名
        self.ranks = self.ranks[0:self.p.num_volume]

        # 对于上期入选的股票，本次不入选则先进行平仓
        sell_list = set(self.lastStock) - set(self.ranks)

        # 处理股票池中的股票
        self.handel_order(self.ranks, self.order_list,sell_list)

        # 跟踪上次买入的股票列表
        self.lastStock = self.ranks

    # 进行选股
    def filter_stocks(self, codeList):
        selected_datas = [data for data in self.datas if data._name in codeList]
        print(f"筛选后的数据源长度：{len(selected_datas)}")
        return selected_datas
