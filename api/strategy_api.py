from flask import Blueprint
from entity.base_cerebro_data import BaseCerebroData
from startegy.factor_stock_strategy import FactorStockStrategy
from startegy.michael_sivy_strategy import MichaelSivyStrategy
from startegy.strategy_data.michael_sivy_data import MichaelSivyData
from startegy.strategy_data.factor_data import FactorData
from util.analyser import Analyzer
from util.data import BackTestData
import util.constant as CONSTANT
import glob
import os
import datetime
from startegy.cerebro.cerebro import BaseCerebro
strategy = Blueprint('strategy', __name__, url_prefix='/strategy')


@strategy.route('/factor', methods=['POST'])
def factor_choose():
    # 将目录datadir之中的数据加载进系统之中
    fromdate = datetime.datetime(2024, 1, 2)
    todate = datetime.datetime(2024, 4, 26)
    base_data = BaseCerebroData(10000000, 0.001, 0.001, fromdate, todate)
    factor_data = FactorData(base_args=base_data)
    cerebro = BaseCerebro(base_args=base_data, abstract_data=factor_data, strategy_name=FactorStockStrategy)
    result = cerebro.run()
    # 防止下单时现金不够被拒绝，只在执行时检查现金够不够
    analyze = BackTestData(Analyzer(result))
    json_data = analyze.get_json_data(log=True)
    return json_data


@strategy.route('/michaelSivy', methods=['POST'])
def michaelSivy_choose():
    # datadir = CONSTANT.DEFAULT_DIR + '/micsiv_testdata'
    # datadir = CONSTANT.TEST_DATA_DIR + '/MicSivData'
    # datafilelist = glob.glob(os.path.join(datadir, '*.csv'))
    # 将目录datadir之中的数据加载进系统之中
    fromdate = datetime.datetime(2023, 10, 1)
    todate = datetime.datetime(2024, 4, 26)
    base_data = BaseCerebroData(10000000, 0.001, 0.001, fromdate, todate)
    michael_sivy_data = MichaelSivyData(base_data)
    cerebro = BaseCerebro(base_data,abstract_data=michael_sivy_data, strategy_name=MichaelSivyStrategy)
    result = cerebro.run()
    # 定义分析器
    # 防止下单时现金不够被拒绝，只在执行时检查现金够不够
    analyze = BackTestData(Analyzer(result))
    json_data = analyze.get_json_data(log=True)
    return json_data

