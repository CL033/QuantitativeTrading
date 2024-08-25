from entity.base_cerebro_data import BaseCerebroData
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
test_Oshaughnessy()
