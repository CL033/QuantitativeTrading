import backtrader as bt
import pandas as pd
from entity.Oshaughnessy_data import *
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
csv_files_dir = CONSTANT.DEFAULT_DIR + "/OShaughnessy/dailyData2"
csv_folder_path = CONSTANT.DEFAULT_DIR + '/OShaughnessy/reportData'


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

def cfps_filter(stock_data, report_data):
    """
    stock_data：每日股票数据
    report_data：年报数据
     筛选股票
     1. 每股现金流量>=0的股票，股价现金流量比小于平均值
     2. 每股营收>=0的股票，股价营收比小于平均值2/3
     3. 总市值大于平均市值,总股本大于平均值
    """
    selected_stocks = [d for d in stock_data if len(d) > 0]
    if not selected_stocks:
        return []
    if report_data is not None:
        print(f"report length:{len(report_data)}")
        # 过滤并合并股票数据和年报数据
        selected_codes = {d._name for d in selected_stocks}
        report_data = report_data[report_data['ts_code'].isin(selected_codes)]
        print(f"年报长度{len(report_data)}")
        stocks_df = pd.DataFrame([{
            'ts_code': d._name,
            'total_mv': d.total_mv[0],
            'total_share': d.total_share[0],
            'close': d.close[0]
        } for d in selected_stocks])
        stock_data_filter = pd.merge(report_data, stocks_df, on='ts_code', how='inner').drop_duplicates(subset=['ts_code'], keep='first')
        print("======================开始筛选========================\n")

        print("===========第一次筛选（总市值大于平均值)==================\n")
        # 筛选出总市值大于平均市值
        avg_total_mv = stock_data_filter['total_mv'].mean()
        stock_data_filter = stock_data_filter[stock_data_filter['total_mv'] > avg_total_mv]

        # 每股现金流量>=0的股票，股价现金流量比小于平均值
        print("======================第二次筛选======================\n")
        # 剔除现金流量小于0的股票
        stock_data_filter = stock_data_filter[(stock_data_filter['cfps'] > 0)]
        # 计算每个股票的股价现金流量比（P/CF）
        stock_data_filter['p_to_cf_ratio'] = stock_data_filter['close'] / stock_data_filter['cfps']
        # 计算平均值
        average_p_to_cf_ratio = stock_data_filter['p_to_cf_ratio'].mean()
        # 选出小于平均值的股票
        stock_data_filter = stock_data_filter[(stock_data_filter['p_to_cf_ratio'] < average_p_to_cf_ratio)]

        # 总股本大于平均值
        print("======================第三次筛选======================\n")
        avg_total_share = stock_data_filter['total_share'].mean()
        stock_data_filter = stock_data_filter[stock_data_filter['total_share'] > avg_total_share]

        # 每股营收>=0的股票，股价营收比小于平均值2/3
        print("======================第四次筛选======================\n")
        # 每股营收 = 总营收/总股本
        # 总股本 total_share
        stock_data_filter['total_share'] = stock_data_filter['net_cash_flow_operat_act'] / stock_data_filter['cfps']
        stock_data_filter = stock_data_filter[
            (stock_data_filter['total_share'] != 0) & (stock_data_filter['total_share'].notna())]
        # 计算每股营收 = 总营收/总股本
        stock_data_filter['revenue_per_share'] = stock_data_filter['total_operat_income'] / stock_data_filter[
            'total_share']
        # 剔除每股营收小于0
        stock_data_filter = stock_data_filter[(stock_data_filter['revenue_per_share'] > 0)]
        # # 计算股价营收比（P/S Ratio）
        stock_data_filter['p_to_s_ratio'] = stock_data_filter['close'] / stock_data_filter['revenue_per_share']
        # 平均值
        average_p_to_s_ratio = stock_data_filter['p_to_s_ratio'].mean()
        stock_data_filter = stock_data_filter[(stock_data_filter['p_to_s_ratio'] < (2 / 3) * average_p_to_s_ratio)]

        return [d for d in selected_stocks if d._name in stock_data_filter['ts_code'].values]
    else:
        return []


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


class OShaughnessyStrategy(BaseStrategy):
    params = dict(
        num_volume=30  # 取股息率前30名
    )

    def __init__(self):
        super().__init__()
        # 定时器
        self.add_timer(
            when=bt.Timer.SESSION_START,
            allow=QuarterEndChecker()
        )
        # 最后一天时间，即数据的最后一天
        if self.data.datetime.date(0) is not None:
            self.data_end_date = self.data.datetime.date(0)
            self.day_before_end_date = self.data_end_date - timedelta(days=1)

    def prenext(self):
        self.next()

    def next(self):
        print("%s，市值：%.2f" % (self.datetime.date(),self.broker.getvalue()))
        if self.data.datetime.date(0) == self.day_before_end_date:
            print(f"前一天处理订单{self.day_before_end_date}\n")
            # 前一天还有股票，第二天全部卖出
            if self.last_stocks:
                self.handel_order(sell_data_list=self.last_stocks)
        if self.data.datetime.date(0) == self.data_end_date:  # 当前时间是否是最后一天
            # 根据策略判断最后一天入选股票，并且返回
            # 提取月份和年
            year = self.data_end_date.year
            month = self.data_end_date.month
            if 3 <= month <= 5:
                quarter = "q1"
            elif 6 <= month <= 8:
                quarter = "q2"
            elif 9 <= month <= 11:
                quarter = "q3"
            else:
                quarter = "annual"
                # 读取年报数据文件
            filename = f"{year}_{quarter}.csv"
            csv_file_path = os.path.join(csv_folder_path, filename)
            # 检查文件是否存在再尝试读取
            if os.path.exists(csv_file_path):
                df = pd.read_csv(csv_file_path).dropna(how='all')
                print(f"成功读取了日期为 {filename} 的数据")
            else:
                raise FileNotFoundError(f"未找到日期为 {filename} 的CSV文件")
            end_stock = cfps_filter(self.datas, df)
            # 最后一天入选的股票
            for d in end_stock:
                csv_file_name = f"{d._name}.csv"
                csv_file_path = os.path.join(csv_files_dir, csv_file_name)
                df = pd.read_csv(csv_file_path, encoding='utf-8')
                # match_rows = df[df['date'] == self.data.datetime.date(0)]
                df['trade_date'] = pd.to_datetime(df['trade_date'])
                match_rows = df[df['trade_date'].dt.strftime('%Y%m%d') == self.data_end_date.strftime('%Y%m%d')]
                if not match_rows.empty:
                    code = match_rows['ts_code'].iloc[0]
                    name = self.code_name_dict.get(code, "NULL")
                    open = match_rows['open'].iloc[0]
                    high = match_rows['high'].iloc[0]
                    low = match_rows['low'].iloc[0]
                    close = match_rows['close_x'].iloc[0]
                    volume = match_rows['vol'].iloc[0]
                    dv_ratio = match_rows['dv_ratio'].iloc[0]
                    total_share = match_rows['total_share'].iloc[0]
                    total_mv = match_rows['total_mv'].iloc[0]
                    stock_info = StockInfo(code, name, open, high, low, close, volume, dv_ratio, total_share, total_mv
                                           ).to_dict()
                    self.choose_stock_df.append(stock_info)

    def notify_timer(self, timer, when, *args, **kwargs):
        print("%s，市值：%.2f" % (self.data0.datetime.date(0), self.broker.getvalue()))
        self.stock_state_list = []
        # 判断当前日期是否是回测的最后一天，最后一天不进行调仓处理
        if when != self.data_end_date:
            self.rebalanced_portfolio(self.data0.datetime.date(0))  # 进行持仓调整

    # 进行调仓
    def rebalanced_portfolio(self, current_date):
        adjusted_date = get_adjusted_date(current_date)
        # 提取月份和年
        year = adjusted_date.year
        month = adjusted_date.month
        if 3 <= month <= 5:
            quarter = "q1"
        elif 6 <= month <= 8:
            quarter = "q2"
        elif 9 <= month <= 11:
            quarter = "q3"
        else:
            quarter = "annual"

        # 读取年报数据文件
        filename = f"{year}_{quarter}.csv"
        csv_file_path = os.path.join(csv_folder_path, filename)
        # 检查文件是否存在再尝试读取
        if os.path.exists(csv_file_path):
            df = pd.read_csv(csv_file_path).dropna(how='all')
            # print(f"成功读取了日期为 {filename} 的数据")
            # df = pd.read_csv(csv_file_path).fillna(0)
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
        ranks = cfps_filter(self.datas, df)
        print(f"年报最终筛选Code：{len(ranks)}")

        # 按股息率从大到小排序
        ranks.sort(key=lambda d: d.dv_ratio, reverse=True)

        # 取前 num_volume名
        ranks = ranks[0:self.p.num_volume]

        # 对于上期入选的股票，本次不入选则先进行平仓
        sell_list = set(self.last_stocks) - set(ranks)

        # 处理股票池中的股票
        self.handel_order(ranks, self.order_lists, sell_list)
