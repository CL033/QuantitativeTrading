from pathlib import Path

from entity.base_cerebro_data import BaseCerebroData
from query.vanna_sql import Vanna_SQL
from sql.graph.search_garph import SearchGraph
from startegy.OShaughnessy_strategy import OShaughnessyStrategy
from startegy.strategy_data.OShaughnessy_data import *

from util.data import BackTestData
import datetime
from startegy.cerebro.cerebro import BaseCerebro
from util.data import StockInfo
import pandas as pd
from tqdm import tqdm


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


def TestSQLTrain():
    vanna_sql = Vanna_SQL()
    vanna_sql.train(question="市销率>0",
                    sql="SELECT * FROM `backtest_data` WHERE ps > 0 AND "
                        "trade_date = (SELECT MAX(trade_date) FROM `backtest_data`)")
    # current_dir = Path(os.path.abspath(__file__)).parent.parent / 'query' / 'util' / 'train_data' / 'indu_table_creates'
    # for file_name in os.listdir(current_dir):
    #     if file_name.endswith('.txt'):
    #         file_path = current_dir / file_name  # 使用Path对象来构建路径
    #         # 读取文件内容并输出
    #         with open(file_path, 'r', encoding='utf-8') as file:
    #             content = file.read()
    #             vanna_sql.train(ddl=content)


def TestSQLQuery():
    vanna_sql = Vanna_SQL()
    file_path = Path(os.path.abspath(__file__)).parent / 'test_file' / 'sql_test2.xlsx'
    print(file_path)
    # file_path = 'your_excel_file.xlsx'  # 替换为你的 Excel 文件路径
    df = pd.read_excel(file_path, engine='openpyxl')

    # 创建一个空列表来存储查询结果
    results = []

    # 遍历每一行的“样例”数据
    for index, row in tqdm(df.iterrows(), total=df.shape[0], desc="Processing queries"):
        sample_query = row['样例']

        # 执行查询
        result = vanna_sql.query(sample_query)

        # 将结果添加到列表中
        results.append(result)

    # 将结果列表写回“答案”列
    df['本地模型回答'] = results

    # 保存修改后的 DataFrame 回到 Excel 文件
    df.to_excel(file_path, index=False, engine='openpyxl')
    # result = vanna_sql.query("市销率低于20倍的股票")
    # print(result)
    # result = vanna_sql.query("市销率>0,市盈率TTM大于10")
    # print(result)


if __name__ == '__main__':
    vanna_sql = Vanna_SQL()
    search = SearchGraph()
    query_text = "收盘价小于0"
    result = vanna_sql.query(search.replace_fields(query_text))
    print(result)
    # TestSQLTrain()
    # TestSQLQuery()
