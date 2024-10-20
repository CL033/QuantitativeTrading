from entity.base_cerebro_data import BaseCerebroData
from query.vanna_sql import Vanna_SQL
from startegy.OShaughnessy_strategy import OShaughnessyStrategy
from startegy.strategy_data.OShaughnessy_data import *

from util.data import BackTestData
import datetime
from startegy.cerebro.cerebro import BaseCerebro


def test_Oshaughnessy():
    global fromdate, todate, result
    starttime = datetime.datetime.now()
    fromdate = datetime.datetime(2023, 6, 1)
    todate = datetime.datetime(2024, 4, 26)
    base_data = BaseCerebroData(10000000, 0.001, 0.001, fromdate, todate)
    oshaughnessy_data = OshaughnessyData(base_data)
    cerebro = BaseCerebro(base_data, abstract_data=oshaughnessy_data, strategy_name=OShaughnessyStrategy)
    result = cerebro.run()
    # 定义分析器
    # 防止下单时现金不够被拒绝，只在执行时检查现金够不够
    analyze = BackTestData(result)
    json_data = analyze.get_json_data(log=True)
    endtime = datetime.datetime.now()
    print(f"Time: {endtime}")


def testsql():
    vanna_sql = Vanna_SQL()
    # vanna_sql.appRun()
    # vanna_sql.train(documentation="返回的字段只要 ‘id’,‘ts_code’,‘close_x’ 再加上查询的字段即可")
    # vanna_sql.train(
    #     question="市盈率>0,市销率ps>-0.6",
    #     sql="SELECT id,code,close,ps,pe FROM daily where ps>-0.6 and pe>0"
    # )
    result = vanna_sql.query("辰光医疗去年的员工数量")
    print(result)
    # result = vanna_sql.query("市销率>0,市盈率TTM大于10")
    # print(result)
testsql()


