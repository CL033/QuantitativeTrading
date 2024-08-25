import backtrader as bt
import pandas as pd
from entity.michael_sivy_data import *
import util.constant as CONSTANT
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
# 股票数据路径
csv_files_dir = CONSTANT.DEFAULT_DIR + "/MicSivy/MicSivyData"
csv_folder_path = CONSTANT.DEFAULT_DIR + '/MicSivy/new'


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


def michael_sivy_filter(stock_data):
    if stock_data is not None:
        average_equity_ratio = stock_data['equity_ratio'].mean()
        average_current_ratio = stock_data['current_ratio'].mean()

        # 筛选符合条件的行：equity_ratio大于平均equity_ratio且current_ratio小于平均current_ratio
        selected_rows = stock_data.query(
            'equity_ratio > @average_equity_ratio and current_ratio < @average_current_ratio')
        # 提取对应的code
        selected_codes = selected_rows['code'].tolist()

    return selected_codes


class QuarterEndChecker(object):
    """
    自定义定时器，每个季度触发，如果是休息日则继续往后延续直到第一个工作日
    """

    def __init__(self):
        self.comparison_dates = [(3, 31), (6, 30), (9, 30), (12, 31)]
        self.current_date = (-1, -1)

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
        return any((month, day) == self.current_date for month, day in self.comparison_dates)


class MichaelSivyStrategy(BaseStrategy):
    params = dict(
        num_volume=10  # 取成交量前100名
    )

    def __init__(self):
        super().__init__(
            # 定时器
            QuarterEndChecker()
        )
        # 最后一天时间，即数据的最后一天
        if self.data.datetime.date(0) is not None:
            self.data_end_date = self.data.datetime.date(0)
            self.day_before_end_date = self.data_end_date - timedelta(days=1)

    def next(self):

        if self.data.datetime.date(0) == self.day_before_end_date:
            print(f"前一天处理订单{self.day_before_end_date}\n")
            # 前一天还有股票，第二天全部卖出
            if self.last_stocks:
                self.handel_order(sell_data_list=self.last_stocks)
        if self.data.datetime.date(0) == self.data_end_date:  # 当前时间是否是最后一天
            adjusted_date = get_adjusted_date(self.data_end_date)
            filename = adjusted_date.strftime('%Y%m%d')  # 格式化日期为 YYYYMMDD
            # 读取年报数据文件
            filename = filename + '.csv'
            csv_file_path = os.path.join(csv_folder_path, filename)

            # 检查文件是否存在再尝试读取
            if os.path.exists(csv_file_path):
                df = pd.read_csv(csv_file_path).fillna(0)
                print(f"成功读取了日期为 {filename} 的数据")
            else:
                raise FileNotFoundError(f"未找到日期为 {filename} 的CSV文件")
            ranks = michael_sivy_filter(df)
            ranks = self.filter_stocks(ranks)
            for d in ranks:
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
                    change = match_rows['change'].iloc[0]
                    stock_info = StockInfo(code, name, open, high, low, close, volume, amount, change
                                           ).to_dict()
                    self.choose_stock_df.append(stock_info)

    def notify_timer(self, timer, when, *args, **kwargs):
        self.stock_state_list = []
        if when != self.data_end_date:
            self.rebalanced_portfolio()  # 进行持仓调整

    # 进行调仓
    def rebalanced_portfolio(self):
        print(self.data0.datetime.date(0))
        current_date = self.data0.datetime.date(0)
        adjusted_date = get_adjusted_date(current_date)
        filename = adjusted_date.strftime('%Y%m%d')  # 格式化日期为 YYYYMMDD
        # 读取年报数据文件
        filename = filename + '.csv'
        csv_file_path = os.path.join(csv_folder_path, filename)

        # 检查文件是否存在再尝试读取
        if os.path.exists(csv_file_path):
            df = pd.read_csv(csv_file_path).fillna(0)
            print(f"成功读取了日期为 {filename} 的数据")
        else:
            raise FileNotFoundError(f"未找到日期为 {filename} 的CSV文件")

        if len(self.data0) > 0:
            self.currDate = self.data0.datetime.date(0)
        else:
            self.log('警告：数据源data0为空，无法获取初始日期')
        if len(self.datas[0]) == self.data0.buflen():
            return
        # 取消以往所下的订单（对于已经成交的不生效）
        for o in self.order_lists:
            self.cancel(o)
        # 重置订单列表
        self.order_lists = []
        # 最终选取结果
        ranks = michael_sivy_filter(df)
        print(f"code：{len(ranks)}")
        # print(str(self.ranks))
        ranks = self.filter_stocks(ranks)
        # print(str(self.ranks))

        # 按成交量从大到小排序
        ranks.sort(key=lambda d: d.volume, reverse=True)

        # 取前 num_volume名
        ranks = ranks[0:self.p.num_volume]

        # 对于上期入选的股票，本次不入选则先进行平仓
        sell_list = set(self.last_stocks) - set(ranks)

        # 处理股票池中的股票
        self.handel_order(ranks, self.order_lists, sell_list)

    # 进行选股
    def filter_stocks(self, code_list):
        selected_datas = [data for data in self.datas if data._name in code_list]
        print(f"筛选后的数据源长度：{len(selected_datas)}")
        return selected_datas
