import os
from pathlib import Path
from vanna.chromadb import ChromaDB_VectorStore
from vanna.qianwen import QianWenAI_Chat
import util.constant as CONSTANT
import re
from util.data import StockInfo
from vanna.flask import VannaFlaskApp
import pymysql
import pandas as pd


class Myvanna(ChromaDB_VectorStore, QianWenAI_Chat):
    def __init__(self, config=None):
        ChromaDB_VectorStore.__init__(self, config=config)
        QianWenAI_Chat.__init__(self, config=config)


class Vanna_SQL:
    def __init__(self):
        self.vn = Myvanna(
            config={
                "model": "qwen1.5-14b-chat",
                "temperature": 0,
                "api_key": CONSTANT.DASHSCOPE_API_KEY,
                "path": f'{str(Path(os.path.abspath(__file__)).parent)}/vectorStore'
            })
        # 连接mysql数据库
        self.vn.connect_to_mysql(
            host=CONSTANT.DB_HOST,
            dbname=CONSTANT.DB_DATABASE,
            user=CONSTANT.DB_USER,
            password=CONSTANT.DB_PASSWORD,
            port=3306)
        pymysql.install_as_MySQLdb()
        db_config = {
            'host': CONSTANT.DB_HOST,
            'user': CONSTANT.DB_USER,
            'password': CONSTANT.DB_PASSWORD,
            'database': CONSTANT.DB_DATABASE,
        }
        self.connection = pymysql.connect(**db_config)
        # self.vn.run_sql = self.run_sql
        # self.vn.run_sql_is_set = True


    # 模型训练
    def train(self, question: str = None, sql: str = None, ddl: str = None, documentation: str = None):
        if documentation:
            self.vn.train(documentation=documentation)
            print("Document新增训练完成")
        if question and sql:
            self.vn.train(question=question, sql=sql)
            print("SQL问题对新增训练完成")
        if ddl:
            self.vn.train(ddl=ddl)
            print("DDL新增训练完成")

    def run_sql(self, sql: str):
        df = pd.read_sql(sql, self.connection)
        dict_results = [StockInfo(**row).to_dict() for row in df.to_dict(orient='records')]
        return dict_results

    def ask(self,question:str):
        answer = self.vn.ask(question=question)
        return answer

    def query(self, question: str):

        answer = self.vn.generate_sql(question=question,allow_llm_to_see_data=True)
        return answer
        print("模型输出", answer+"limit 10")
        # pattern = r"(?i)WHERE\s+.*?(?=\s+LIMIT|\;|$)"
        # match = re.search(pattern, answer, re.IGNORECASE)
        # if match:
        # where_condition = match.group(0)
        # sql_condition = f"select * from {CONSTANT.TABLE} {where_condition};"
        # print(sql_condition)
        try:

            with self.connection.cursor() as cursor:
                print(answer+" limit 10")
                # 执行查询
                # sql = "YOUR SQL QUERY HERE"
                cursor.execute(answer+" limit 10")

                # 获取列名
                column_names = [desc[0] for desc in cursor.description]

                # 获取查询结果
                results = cursor.fetchall()

                # 将结果转换为字典列表
                # dict_results = [dict(map(lambda item: (item[0], convert_date(item[1])), zip(column_names, row)))
                #                 for row in results]/# 使用 DataObject 类和 to_dict 方法处理查询结果
                dict_results = [StockInfo(**dict(zip(column_names, row))).to_dict() for row in results]
                print("数据", dict_results)
                return dict_results
        except Exception as e:
            raise e
        # else:
        #     return None

    def appRun(self):
        VannaFlaskApp(self.vn).run()

    def getTrain(self):
        training_data = self.vn.get_training_data()
        print(training_data)


if __name__ == "__main__":
    # print("结构",answer)

    vanna_sql = Vanna_SQL()
    # vanna_sql.train(documentation="如果问题里面没有时间，则以当前时间为主；如果有，则进行格式转化位 ’YYYY-MM-DD HH:MM:SS‘ 的格式；"
    #                               "如果遇到像’前一天‘这种关键词，则获取当前时间再减1；如果是’往前10天‘，则获取当前时间再减十天"
    #                              )
    # vanna_sql.train(question="辰光医疗去年的员工数量",sql="SELECT number FROM personal_salary "
    #                                            "WHERE company_name = '辰光医疗' AND year = YEAR(CURDATE()) - 1"
    #                                            )
    vanna_sql.appRun()

    # vanna_sql.train(
    #     question="市盈率>0,市销率ps>-0.6",
    #     sql="SELECT id,code,close,ps,pe FROM daily where ps>-0.6 and pe>0"
    # )
    # vanna_sql.train(documentation="返回的字段只要 ‘id’,‘ts_code’,‘close_x’ 再加上查询的字段即可")
    # vanna_sql.appRun()

    # response = vanna_sql.query("市盈率>0，市销率ps>-0.6")
    # response = vanna_sql.query("市销率>0,市盈率TTM大于10")
    # print(response)
    # 遍历输出目录中的所有.txt文件

    # current_dir = Path(os.path.abspath(__file__)).parent / 'util' / 'train_data' / 'indu_table_creates'
    # # 遍历输出目录中的所有.txt文件
    # for file_name in os.listdir(current_dir):
    #     if file_name.endswith('.txt'):
    #         file_path = current_dir / file_name  # 使用Path对象来构建路径
    #         # 读取文件内容并输出
    #         with open(file_path, 'r', encoding='utf-8') as file:
    #             content = file.read()
    #             vanna_sql.train(ddl=content)
