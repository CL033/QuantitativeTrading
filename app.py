from collections import defaultdict

from flask import Flask, request, jsonify
from flask_cors import CORS
from entity.base_cerebro_data import BaseCerebroData
from startegy.factor_stock_strategy import FactorStockStrategy
from startegy.michael_sivy_strategy import MichaelSivyStrategy
from analysis.analyser import Analyzer
from util.data import BackTestData
import glob
import os
from strategy_start.base_start import *
from strategy_start.michael_sivy import *

app = Flask(__name__)
app.config['host'] = '192.168.1.6'

CORS(app, supports_credentials=True) # 允许跨域访问

@app.route('/')
def hello_world():  # put application's code here
    return 'Hello aa !'

@app.route('/chooseStock',methods=['POST'])
def ChooseStockPool():
    datadir = 'D:/Pycharm/Workplace/Trader/stockData/change'
    datafilelist = glob.glob(os.path.join(datadir, '*.csv'))
    # 将目录datadir之中的数据加载进系统之中
    fromdate = datetime.datetime(2024,4,20)
    todate = datetime.datetime(2024,4,26)
    base_data = BaseCerebroData(10000000, 0.001, 0.001,fromdate,todate)
    result = Cerebrorun(base_data, datafilelist, FactorStockStrategy)
    # 防止下单时现金不够被拒绝，只在执行时检查现金够不够
    analyze = BackTestData(Analyzer(result))
    json_data = analyze.get_json_data(log=True)
    return json_data

@app.route('/michael_sivy_chooseStock',methods=['POST'])
def Michael_sivy_choose_ChooseStockPool():
    datadir = '/home/c/Downloads/QuantitativeTrading/stockData/micsiv_testdata'
    datafilelist = glob.glob(os.path.join(datadir, '*.csv'))
    # 将目录datadir之中的数据加载进系统之中
    fromdate = datetime.datetime(2023,1,1)
    todate = datetime.datetime(2024,4,26)
    base_data = BaseCerebroData(10000000, 0.001, 0.001,fromdate,todate)
    result = Cerebrorun1(base_data, datafilelist, MichaelSivyStrategy)
    # 防止下单时现金不够被拒绝，只在执行时检查现金够不够
    analyze = BackTestData(Analyzer(result))
    json_data = analyze.get_json_data(log=True)
    return json_data

if __name__ == '__main__':
    app.run(debug=True)
