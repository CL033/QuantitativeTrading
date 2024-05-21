import pyfolio as pf
from pyecharts.charts import *
from pyecharts import options as opts
from util.calculate import *
from util.code_util import *
from decimal import Decimal, ROUND_HALF_UP

class Analyzer():
    def __init__(self, result):
        if len(result)>0:
            self.result = result[0]
            pd.set_option('display.float_format', '{:.4f}'.format)
            self.pnl = pd.Series(result[0].analyzers._TimeReturn.get_analysis())
            pd.set_option('display.max_rows', None)  # 显示所有行
            pd.set_option('display.max_columns', None)  # 显示所有列
            pd.set_option('display.width', None)  # 自动调整宽度
            pd.set_option('display.max_colwidth', 100)  # 设置每列最大宽度



            self.syl, self.drawback = get_return_rate_from_pnl(self.pnl)
            # print(self.drawback)
            self.start_time = self.syl.index[0].strftime("%Y%m%d")
            self.end_time = self.syl.index[-1].strftime("%Y%m%d")
            self.perf_stats_all = pf.timeseries.perf_stats((self.pnl)).to_frame(name='all')

            self.perf_stats_all = self.perf_stats_all.applymap(round_to_four_decimal_places)
            self.perf_stats_all.index = ['年化收益率', '累计收益率', '年化波动率', '夏普率', '卡玛比率', '稳定度', '最大回撤', '欧米伽比率', '索提诺比率', '偏度',
                                         '峰度', 'tail 比率', '每日风险价值']

    # 绘制收益率图
    def plot_syl(self):
        syl = self.syl
        start = self.start_time
        end = self.end_time

        # 选项卡
        cate = index.keys()

        # 新建一个tab对象
        tab = Tab()
        for c in cate:
            code = index[c]
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

