import backtrader as bt
from startegy.strategy_data.abstract_data import AbstractData
from util.analyser import Analyzer

class stockCommissionScheme(bt.CommInfoBase):
    params = (
        ('stamp_duty', 0.005),
        ('commission', 0.001),
        ('stocklike', True),
        ('commtype', bt.CommInfoBase.COMM_PERC)
    )

    def _getcommission(self, size, price, pseudoexec):
        if size > 0:
            return size * price * self.p.commission
        elif size < 0:
            return size * price * (self.p.stamp_duty + self.p.commission)
        else:
            return 0


class BaseCerebro:
    def __init__(self, base_args, abstract_data: AbstractData, strategy_name):
        """
        base_args：基础信息(BaseData)
        abstract_data：股票列表数据
        strategy_name：回测策略
        """
        self.base_args = base_args
        self.abstract_data = abstract_data
        self.strategy_name = strategy_name
        pass

    def run(self):
        cerebro = bt.Cerebro()
        # 添加观测器
        cerebro.addobserver(bt.observers.Broker)
        cerebro.addobserver(bt.observers.Trades)
        # 加载股票的列表数据
        self.abstract_data.read_data(cerebro)
        # 设置股票现金等参数
        cerebro.broker.setcash(self.base_args.start_cash)
        # 防止下单时现金不够被拒绝，只在执行时检查现金够不够
        cerebro.broker.set_checksubmit(False)
        # 添加印花税率等参数
        comminfo = stockCommissionScheme(stamp_duty=self.base_args.stamp_duty, commission=self.base_args.commission)
        cerebro.broker.addcommissioninfo(comminfo)

        # 添加分析器
        # 返回年初至年末的年度收益率
        cerebro.addanalyzer(bt.analyzers.AnnualReturn, _name='_AnnualReturn')
        # 计算年化夏普比率
        cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='_SharpeRatio')
        # 计算最大回撤相关指标
        cerebro.addanalyzer(bt.analyzers.DrawDown, _name='_DrawDown')
        # 计算年化收益
        cerebro.addanalyzer(bt.analyzers.Returns, _name='_Returns', tann=252)
        # 返回收益率时序
        cerebro.addanalyzer(bt.analyzers.TimeReturn, _name='_TimeReturn')
        cerebro.addanalyzer(bt.analyzers.PyFolio, _name='_PyFolio')

        # 添加策略
        cerebro.addstrategy(self.strategy_name)
        # 返回结果
        result = cerebro.run(runonce=False)
        # 数据分析
        analyzer = Analyzer(result)
        # print(result)
        return analyzer
