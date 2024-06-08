from flask import Flask, Blueprint, request, jsonify
from entity.base_cerebro_data import BaseCerebroData
from startegy.factor_stock_strategy import FactorStockStrategy
from startegy.michael_sivy_strategy import MichaelSivyStrategy
from analysis.analyser import Analyzer
from util.data import BackTestData
import util.constant as CONSTANT
import glob
import os
from strategy_start.base_start import *
from strategy_start.michael_sivy import *
strategy = Blueprint('strategy', __name__, url_prefix='/strategy')


@strategy.route('/factor', methods=['POST'])
def factor_choose():
    datadir = CONSTANT.TEST_DATA_DIR + '/factory_strategy_data'
    datafilelist = glob.glob(os.path.join(datadir, '*.csv'))
    # 将目录datadir之中的数据加载进系统之中
    fromdate = datetime.datetime(2024, 1, 2)
    todate = datetime.datetime(2024, 4, 26)
    base_data = BaseCerebroData(10000000, 0.001, 0.001, fromdate, todate)
    result = cerebro_run(base_data, datafilelist, FactorStockStrategy)
    # 防止下单时现金不够被拒绝，只在执行时检查现金够不够
    analyze = BackTestData(Analyzer(result))
    json_data = analyze.get_json_data(log=True)
    return json_data


@strategy.route('/michaelSivy', methods=['POST'])
def michaelSivy_choose():
    # datadir = CONSTANT.DEFAULT_DIR + '/micsiv_testdata'
    datadir = CONSTANT.TEST_DATA_DIR + '/MicSivData'
    datafilelist = glob.glob(os.path.join(datadir, '*.csv'))
    # 将目录datadir之中的数据加载进系统之中
    fromdate = datetime.datetime(2023, 1, 1)
    todate = datetime.datetime(2024, 4, 26)
    base_data = BaseCerebroData(10000000, 0.001, 0.001, fromdate, todate)
    result = Cerebrorun1(base_data, datafilelist, MichaelSivyStrategy)
    # 防止下单时现金不够被拒绝，只在执行时检查现金够不够
    analyze = BackTestData(Analyzer(result))
    json_data = analyze.get_json_data(log=True)
    return json_data
