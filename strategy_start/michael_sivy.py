import tempfile

import backtrader as bt
from tqdm import tqdm
import pandas as pd
import datetime


class stockCommissionScheme(bt.CommInfoBase):
    params = (
        ('stamp_duty', 0.005),  # ??????
        ('commission', 0.001),  # ?????
        ('stocklike', True),
        ('commtype', bt.CommInfoBase.COMM_PERC)
    )

    def _getcommission(self, size, price, pseudoexec):
        if size > 0:  # ??????????????
            return size * price * self.p.commission
        elif size < 0:  # ??????????????
            return size * price * (self.p.stamp_duty + self.p.commission)
        else:
            return 0


# bt.feeds.GenericCSVData
class PandasDataExtend(bt.feeds.GenericCSVData):
    """
    equity_ratio: 产权比率
    current_ratio：流通比率
    pe_ttm：市盈率TTM
    EPS：每股收益增长率
    dv_ratio：股息率
    """

    # lines = ('equity_ratio', 'current_ratio', 'pe_ttm', 'EPS', 'dv_ratio')
    # params = (('equity_ratio', 8),
    #           ('current_ratio', 9),
    #           ('pe_ttm', 10),
    #           ('EPS', 11),
    #           ('dv_ratio', 12))


def Cerebrorun1(base_args, strategy_data_list, strategy_name):
    """
    base_args：基础信息(BaseData)
    strategy_data_list：股票列表数据
    strategy_name：回测策略
    """
    cerebro = bt.Cerebro()
    # 添加观测器
    cerebro.addobserver(bt.observers.Broker)
    cerebro.addobserver(bt.observers.Trades)

    # 添加数据
    print(f"\nLength of strategy_data_list: {len(strategy_data_list)}\n")
    print("\n------------Begin add Datas------------\n")
    for i, fname in enumerate(tqdm(strategy_data_list)):
        # 读取CSV文件
        df = pd.read_csv(
            fname,
            skiprows=0,
            header=0,
            encoding='GBK'
        )

        # 确保日期列名为'datetime'，如果不是，请替换为实际的日期列名
        if 'date' not in df.columns:
            raise ValueError(f"CSV file {fname} does not contain a column named 'datetime'.")

        # 将'datetime'列转换为datetime类型
        df['date'] = pd.to_datetime(df['date'], format='%Y%m%d')

        df = df.dropna()
        # 筛选出符合时间范围的数据
        df = df[(df['date'] >= base_args.fromdate) & (df['date'] <= base_args.todate)]

        if len(df) == 0:
            print('bad ############', fname)
            continue
        # 创建临时文件，用于存储筛选后数据
        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as temp_file:
            df.to_csv(temp_file.name, index=False, encoding='GBK')
        # date_df = pd.read_csv(
        #     fname,
        #     usecols=['date'],
        #     skiprows=0,
        #     header=0,
        #     encoding='GBK'
        # )
        # # 转换
        # date_df['date'] = pd.to_datetime(date_df['date'])
        # # 选出从2024年以后的数据
        # date_df = date_df[date_df['date'] > pd.Timestamp('2024-03-15')]
        # # ???????????????????????????????
        # df = pd.read_csv(
        #     fname,
        #     skiprows=0,  # 不忽略行
        #     header=0,  # 列头在第0行
        #     encoding='GBK'
        # )
        # df = df[df.index.isin(date_df.index)]
        # df = df[['date', 'open', 'close', 'high', 'low', 'volume', 'peTTM', 'pbMRQ', 'psTTM']]
        # df['date'] = pd.to_datetime(df['date'])
        # df.set_index('date', inplace=True)
        # df = df.dropna()  # 删除缺省值
        # df['openinterest'] = 0
        data = PandasDataExtend(
            dataname=temp_file.name,
            fromdate=base_args.fromdate,
            todate=base_args.todate + datetime.timedelta(days=1),
            nullvalue=0.0,
            dtformat=('%Y-%m-%d'),
            datetime=0,
            open=2,
            high=3,
            low=4,
            close=5,
            volume=7,
            openinterest=-1,
            # equity_ratio=9,
            # current_ratio=10,
            # pe_ttm=11,
            # EPS=12,
            # dv_ratio=13,
            plot=False
        )
        ticker = fname[-13:-4]  # 将文件名作为名字
        cerebro.adddata(data, name=ticker)
    print("\n------------Finish add Datas------------!\n")

    # 设置初始资金
    cerebro.broker.setcash(base_args.start_cash)

    # 防止下单时现金不够被拒绝，只在执行时检查现金够不够
    cerebro.broker.set_checksubmit(False)

    # 添加印花税率等参数
    comminfo = stockCommissionScheme(stamp_duty=base_args.stamp_duty, commission=base_args.commission)
    cerebro.broker.addcommissioninfo(comminfo)

    # 添加分析器
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='_SharpeRatio')
    cerebro.addanalyzer(bt.analyzers.TimeReturn, _name='_TimeReturn')
    cerebro.addanalyzer(bt.analyzers.PyFolio, _name='_PyFolio')
    # 添加策略
    cerebro.addstrategy(strategy_name)
    # 返回结果
    result = cerebro.run(runonce=False)
    # print(result)
    return result
