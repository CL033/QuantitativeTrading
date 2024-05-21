import datetime
import decimal
import json
from typing import Any
import pandas
from flask import request


class BaseData:
    def __init__(self, request):
        # com_code 股票代码
        self.com_code = request.form.get('comCode', default='000001').split(',')
        # start_date 回测开始时间
        self.start_date = request.form.get('startDate', default='20200128')
        # end_date 回测结束时间
        self.end_date = request.form.get('endDate', default='20230128')
        #  初始资金
        self.start_cash = int(request.form.get('startCash', default=1000000))
        #  手续费
        self.comm = float(request.form.get('comm', default=0.0005))
        #  印花税
        self.stamp_duty = float(request.form.get('stampDuty', default=0.001))
        #  股票代码复权方式 “qfq” “hfq”
        self.adjust = request.form.get('adjust', default='qfq')
        # slip_perc 滑点比例
        self.slip_perc = float(request.form.get('slipPerc', default=0.0001))
        # 是否为选股模式
        self.choose = False


def strftime_date(df: pandas.DataFrame):
    try:
        df['日期'] = df['日期'].apply(lambda x: x.strftime("%Y-%m-%d"))
    except:
        return df
    return df


class DateEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        # 处理datatime类型的数据
        if isinstance(o, datetime.datetime):
            return o.strftime("%Y-%m-%d %H:%M:%S")
        # 处理date类型的数据
        if isinstance(o, datetime.date):
            return o.strftime("%Y-%m-%d")
        # 处理返回数据中有decimal
        if isinstance(o, decimal.Decimal):
            return float(o)
        return json.JSONEncoder.default(self, o)


class BackTestData:
    def __init__(self, analyse):
        if (analyse is not None):
            perf_stats = analyse.perf_stats_all
            # 相关指标
            self.backtest_indicators = perf_stats.to_dict(orient='dict')
            self.syl_plot = analyse.plot_syl()
            self.log_fund = strftime_date(analyse.result.fund_df).to_dict(orient='dict')
            self.log_stock = strftime_date(analyse.result.stock_df).to_dict(orient='dict')
            self.log_trade = analyse.result.trade_df
            self.stock_pool = strftime_date(analyse.result.choose_stock_df)

    def get_json_data(self, log=True):
        data = {}
        data['indicators'] = self.backtest_indicators['all']

        syl_plot = {}
        for line in self.syl_plot._charts:
            i_chart = json.loads(line.dump_options_with_quotes())
            syl_plot[i_chart['series'][0]['name']] = i_chart
        data['syl_plot'] = syl_plot

        if log == True:
            data['log_fund'] = self.log_fund
            data['log_stock'] = self.log_stock
            data['log_trade'] = self.log_trade
            data['stock_pool'] = self.stock_pool
        data_json = json.dumps(data, ensure_ascii=False, cls=DateEncoder).encode("utf-8")
        return data_json