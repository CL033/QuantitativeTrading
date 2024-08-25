import pyfolio as pf
import akshare as ak
from pyecharts.charts import *
from pyecharts import options as opts
import util.constant as CONSTANT
from decimal import Decimal, ROUND_HALF_UP
import pandas as pd


class Analyzer:
    def __init__(self, result):
        if len(result) > 0:
            self.result = result[0]
            # # 获取每日收益率
            # daily_returns = pd.Series(self.result.analyzers._TimeReturn.get_analysis())
            # # 计算累计收益率
            # self.cumulative_returns = (1 + daily_returns).cumprod() - 1
            # # # 计算回撤率
            # # self.drawdown = self.calculate_drawdown(self.cumulative_returns)

            self.pnl = pd.Series(result[0].analyzers._TimeReturn.get_analysis())
            # # 计算累计收益
            # self.cumulative = (self.pnl + 1).cumprod()

            self.syl, self.drawback = get_return_rate_from_pnl(self.pnl)

            self.start_time = self.syl.index[0].strftime("%Y%m%d")
            self.end_time = self.syl.index[-1].strftime("%Y%m%d")
            self.perf_stats_all = pf.timeseries.perf_stats((self.pnl)).to_frame(name='all')
            print(self.perf_stats_all.index)
            self.perf_stats_all.loc['Annual return'] *= 100
            self.perf_stats_all.loc['Cumulative returns'] *= 100
            self.perf_stats_all.loc['Max drawdown'] *= 100
            # 保留两位小数
            self.perf_stats_all = self.perf_stats_all.applymap(round_to_four_decimal_places)
            self.perf_stats_all.index = ['年化收益率', '累计收益率', '年化波动率', '夏普率', '卡玛比率', '稳定度',
                                         '最大回撤', '欧米伽比率', '索提诺比率', '偏度',
                                         '峰度', 'tail 比率', '每日风险价值']

    # 绘制收益率图
    def plot_syl(self):
        syl = self.syl
        start = self.start_time
        end = self.end_time

        # 选项卡
        cate = CONSTANT.CODE_INDEX.keys()

        # 新建一个tab对象
        tab = Tab()
        for c in cate:
            code = CONSTANT.CODE_INDEX[c]
            df = ak.stock_zh_index_daily_em(symbol=code, start_date=start, end_date=end)
            line = (Line(init_opts=opts.InitOpts(bg_color='white', width='1000px', height='400px'))
                    .add_xaxis(list(df.date.values))
                    .add_yaxis(c, get_return_rate_from_pd(df))
                    .add_yaxis("策略收益率", list(syl.values))
                    .set_global_opts(datazoom_opts=opts.DataZoomOpts(range_start=0, range_end=100),
                                     title_opts=opts.TitleOpts(title="我是主标题", subtitle='我是副标题'),
                                     legend_opts=opts.LegendOpts(is_show=True),
                                     tooltip_opts=opts.TooltipOpts(is_show=True, trigger='axis'),
                                     yaxis_opts=opts.AxisOpts(name='收益率/%'))
                    )
            tab.add(line, c)
        return tab


def round_to_four_decimal_places(value):
    return float(Decimal(str(value)).quantize(Decimal('0.0001'), rounding=ROUND_HALF_UP))


# 根据日收益率序列计算收益率与回撤率
def get_return_rate_from_pnl(pnl: pd.Series):
    cumulative = ((pnl + 1).cumprod() - 1).apply(lambda x: x * 100).round(2)
    # 计算回撤序列
    max_return = cumulative.cummax()
    drawdown = (max_return - cumulative) / max_return
    drawdown.fillna(0, inplace=True)
    drawdown = drawdown.apply(lambda x: x * 100).round(2)

    return cumulative, drawdown


# 根据收盘价计算收益率
def get_return_rate_from_pd(df:pd.DataFrame):
    df['earn_rate'] =( df['close'].pct_change()).apply(lambda x:x*100 ).round(2)
    df['syl']=((1+df['earn_rate']).cumprod()-1).apply(lambda x:x*100 ).round(2)
    return list(df.earn_rate.values)
