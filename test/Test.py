import glob
import os
import pandas as pd
from tqdm import tqdm
import backtrader as bt
from datetime import datetime,time
from backtrader.feeds import PandasData

pd.set_option('display.width', 1000)#加了这一行那表格的一行就不会分段出现了
#显示所有列
pd.set_option('display.max_columns', None)
#显示所有行
pd.set_option('display.max_rows', None)

class PandasDataExtend(PandasData):
    lines = ('peTTM','pbMRQ','psTTM')
    params = (('peTTM',-1),
              ('pbMRQ',-1),
              ('psTTM',-1))


class stockCommissionScheme(bt.CommInfoBase):
    params = (
        ('stamp_duty',0.005), # 印花税率
        ('commission',0.001), # 佣金率
        ('stocklike',True),
        ('commtype',bt.CommInfoBase.COMM_PERC)
    )
    def _getcommission(self, size, price, pseudoexec):
        if size > 0: # 买入，不考虑印花税
            return size * price * self.p.commission
        elif size < 0: # 卖出，考虑印花税
            return size * price * (self.p.stamp_duty+self.p.commission)
        else:
            return 0;
class Strategy(bt.Strategy):
    params = dict(
        rebal_monthday = [2],# 每月日重新执行持仓调整
        num_volume = 100 # 成交量取前100名
    )
    # 日志函数
    def log(self,txt,dt =None):
        # 以第一个数据data0，即指数作为时间标准
        dt = dt or self.data0.datetime.date(0)
        print("%s，%s" % (dt.isoformat(),txt))

    def __init__(self):
        self.lastStock = [] # 上次交易股票的列表
        self.stocks = self.datas
        # 记录以往的订单，在调整之前全部取消未成交的订单
        self.order_list = []

        # 定时器
        self.add_timer(
            when=bt.Timer.SESSION_START,
            monthdays=self.p.rebal_monthday ,# 每个月2号触发
            monthcarry=True # 如果平衡日不是交易日，则顺延触发notify_timer
        )
    def notify_timer(self, timer, when, *args, **kwargs):
        self.rebalance_portfolio() # 执行调整

    def notify_order(self, order):
        if order.status in [order.Submitted,order.Accepted]:
                # 订单状态：submitted/accepted，无动作
            return
            # 订单完成
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log('买单执行，%s，%.2f，%i' % (order.data._name,order.executed.price, order.executed.size))
            elif order.issell():
                self.log('卖单执行，%s，%.2f，%i' % (order.data._name, order.executed.price, order.executed.size))
        else:
            self.log('订单作废，%s，%s，isbuy=%i，size %i,open price %.2f' % (order.data._name, order.getstatusname(), order.isbuy(), order.created.size, order.data.open[0]))

        # 记录交易情况
    def notify_trade(self, trade):
        if trade.isclosed:
            print('毛收益 %0.2f, 扣佣后收益 % 0.2f, 佣金 %.2f, 市值 %.2f, 现金 %.2f' %
                  (trade.pnl, trade.pnlcomm, trade.commission, self.broker.getvalue(), self.broker.getcash()))

    def rebalance_portfolio(self):
        if len(self.data0) > 0:
            self.currDate = self.data0.datetime.date(0)
        else:
            self.log('警告：数据源data0为空，无法获取初始日期')
        print(self.currDate)
        if len(self.datas[0]) ==self.data0.buflen():
            return
        # 取消以往订单（已成交的不起作用）
        for o in self.order_list:
            self.cancel(o)
        self.order_list=[] # 重置
        # 获取股票池
        # self.stockPool = getStockData(self.currDate)
        self.ranks = chooseStock(self.stocks,self.currDate)
        print(self.ranks)
        # # 从股票池进行筛选
        # self.ranks = chooseStock(self.stockPool)
        # 选出成交量在前100的股票
        self.ranks = self.ranks[0:self.p.num_volume]

        data_toclose = set(self.lastStock)-set(self.ranks)
        # 如果股票没入选，则进行平仓处理
        for d in data_toclose:
            print('sell 平仓' ,d._name,self.getposition(d).size)
            o = self.close(data=d)
            self.order_list.append(o) # 记录订单

        # 本次入选的股票
        # 每只股票买入资金百分比，预留2%的资金以应对佣金和计算误差
        if(len(self.ranks)>0):
            buypercentage = (1-0.02)/len(self.ranks)
        else:
            buypercentage = 0

        # 得到目标市值
        targetvalue = buypercentage * self.broker.getvalue()
        self.ranks.sort(key=lambda d: self.broker.getvalue([d]), reverse=True)
        self.log('下单, 目标的股票个数 %i, targetvalue %.2f, 当前总市值 %.2f' %
                 (len(self.ranks), targetvalue, self.broker.getvalue()))

        # 新股票买入
        for d in self.ranks:
            # 按次日开盘价计算下单量，下单量是100的整数倍
            size = int(
                abs((self.broker.getvalue([d]) - targetvalue) / d.open[1] // 100 * 100))
            validday = d.datetime.datetime(1)  # 该股下一实际交易日
            if self.broker.getvalue([d]) > targetvalue:  # 持仓过多，要卖
                # 次日跌停价近似值
                if len(d.close) > 0:
                    print("close",d.close[0])
                    lowerprice = d.close[0] * 0.9 + 0.02

                    o = self.sell(data=d, size=size, exectype=bt.Order.Limit,
                                  price=lowerprice, valid=validday)
            else:  # 持仓过少，要买
                # 次日涨停价近似值
                if len(d.close) > 0:
                    print("close", d.close[0])
                    upperprice = d.close[0] * 1.1 - 0.02
                    o = self.buy(data=d, size=size, exectype=bt.Order.Limit,
                                 price=upperprice, valid=validday)
            if o:
                self.order_list.append(o)  # 记录订单

        self.lastRanks = self.ranks  # 跟踪上次买入的标的




# # 获取某一个日期的股票池数据
def getStockData1(target_date):
    base_dir = '/stockData'
    file_extension = '.csv'
    matched_df = pd.DataFrame()
    print("开始获取\n")
    # 使用tqdm库创建一个进度条
    files_iterator = os.listdir(base_dir)
    progress_bar = tqdm(files_iterator, desc="Processing CSV files:", unit="file")
    for filename in progress_bar:
        if filename.endswith(file_extension):
            # 文件路劲
            file_path = os.path.join(base_dir, filename)

            # 读取CSV文件
            df = pd.read_csv(file_path)
            # print(df)
            if ('date' not in df.columns):
                print(f"Warning: File {filename} does not contrain a 'date' column. Skipping")
                continue
            # 根据日期筛选等于目标日期的行
            # print(type(target_date))

            match_rows = df[df['date'] == target_date]
            print(match_rows)
            matched_df = pd.concat([matched_df, match_rows], ignore_index=True)
    return matched_df


def chooseStock(stockDatas,currentDate):
    selected_stocks = [
        d for d in stockDatas
        if len(d) > 0  # 至少要有一根实际bar
           and d.datetime.date(0) == currentDate
           and d.peTTM >= 10
           and d.peTTM <= 20
           and d.pbMRQ >= 0
           and d.pbMRQ <= 2
           and d.psTTM >= 0
           and d.psTTM <= 1
    ]
    return selected_stocks
# 三低策略筛选方法
def chooseStock1(stockData):
    # target_stock = pd.DataFrame()
    if 'peTTM' not in stockData.columns or 'pbMRQ' not in stockData.columns or 'psTTM' not in stockData.columns:
        raise ValueError("Input DataFrame must have columes 'peTTm' and 'pbMRQ' and 'psTTM'")
    target_stock = stockData[(stockData['peTTM'].between(10,20))&(stockData['pbMRQ'].between(0,2))&(stockData['psTTM'].between(0,1))]
    # 对筛选出的股票进行成交量排序
    target_stock = target_stock.sort_values(by = 'volume',ascending=False)
    target_stock = target_stock.reset_index(drop=True)
    # 把code放入股票池之中
    choosedStock = target_stock['code'].tolist()
    return choosedStock

if __name__ == '__main__':
    # target_date = '2024-04-09'
    # matched_df = getStockData1(target_date)
    # print(len(matched_df))
    #
    # targetStock = chooseStock1(matched_df)
    # print("股票池大小：",len(targetStock),"\n")
    # print(targetStock)
    # print('-------------------')
    # target_date = '2024-02-02'
    # matched_df = getStockData(target_date)
    # print(len(matched_df))
    # targetStock = chooseStock(matched_df)
    # print("股票池大小：", len(targetStock), "\n")
    # print(targetStock)
    ##################
    # 主程序
    ##################
    cerebro = bt.Cerebro()
    cerebro.addobserver(bt.observers.Broker)
    cerebro.addobserver(bt.observers.Trades)
    datadir ='D:/Pycharm/Workplace/Trader/stockData/历史股票数据'
    # datadir = '../stockData'
    datafilelist = glob.glob(os.path.join(datadir,'*.csv'))
    # print(datafilelist)
    # 将目录datadir之中的数据加载进系统之中
    print("----------------------------\n")
    print("开始装载数据，大小是%s\n",len(datafilelist))
    for i,fname in enumerate(tqdm(datafilelist)):
        # 使用useclos只读取'date'列
        date_df = pd.read_csv(
            fname,
            usecols=['date'],
            skiprows=0,
            header=0,
            encoding='GBK'
        )
        # 转换日期格式
        date_df['date'] = pd.to_datetime(date_df['date'])
        # 仅保留2024年以后的数据
        date_df = date_df[date_df['date']>pd.Timestamp('2024-01-01')]
        # 重新读取整个文件，并保留之前筛选出的行
        df = pd.read_csv(
            fname,
            skiprows=0, # 不忽略行
            header=0, # 列头在第0行
            encoding='gbk'
        )
        df = df[df.index.isin(date_df.index)]
        # df.rename(columns={'date' : 'datatime'},inplace=True)
        df = df[['date', 'open', 'close', 'high', 'low', 'volume', 'peTTM', 'pbMRQ', 'psTTM']]
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date',inplace=True)
        # df = df.reset_index(drop=True)
        df =df.dropna() # 删除缺省值

        df['openinterest'] = 0
        # print(df)
        data = PandasDataExtend(
            dataname = df,
            # datetime = 0,
            # open = 2,
            # high = 3,
            # low = 4,
            # close = 5,
            # volume = 6,
            # openinterest = -1,
            fromdate =datetime(2024,1,1),
            todate = datetime(2024,4,9),
            plot = False
        )
        ticker = fname[-13:-4] # 从文件路劲名取得股票代码
        # print('[1]',data.params.dataname.head())
        cerebro.adddata(data,name=ticker)
    print("装载数据完成\n")
    print("----------------------------\n")

    cerebro.addstrategy(Strategy)
    startcash = 10000000
    cerebro.broker.setcash(startcash)
    # 防止下单时现金不够被拒绝，只在执行时检查现金够不够
    cerebro.broker.set_checksubmit(False)
    comminfo = stockCommissionScheme(stamp_duty=0.001, commission=0.001)
    cerebro.broker.addcommissioninfo(comminfo)
    cerebro.addanalyzer(bt.analyzers.AnnualReturn, _name='AnnualReturn')
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='_SharpeRatio')
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='mysharpe')
    cerebro.addanalyzer(bt.analyzers.TimeReturn, _name='_TimeReturn')
    cerebro.addanalyzer(bt.analyzers.PyFolio, _name='pyfolio')
    results = cerebro.run()
    start = results[0]
    print('年收益率：', start.analyzers.AnnualReturn.get_analysis())
    print('夏普比率：', start.analyzers._SharpeRatio.get_analysis())
    print('mysharpe：', start.analyzers.mysharpe.get_analysis())
    print('_TimeReturn：', start.analyzers._TimeReturn.get_analysis())
    print('最终市值：%.2f' % cerebro.broker.getvalue())






