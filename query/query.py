from langchain.chains.sql_database.query import SQLInputWithTables

import util.constant as CONSTANT
from langchain_community.utilities import SQLDatabase
from langchain.chains import create_sql_query_chain
import re
from model.tongyi_online import create_model
from langchain.prompts import ChatPromptTemplate
import pymysql
from collections import OrderedDict
import datetime
import langchain
langchain.debug = True
from langchain_core.runnables import RunnableParallel, RunnablePassthrough

pymysql.install_as_MySQLdb()
# db_config = {
#     'host': CONSTANT.DB_HOST,
#     'user': CONSTANT.DB_USER,
#     'password': CONSTANT.DB_PASSWORD,
#     'database': CONSTANT.DB_DATABASE,
# }
#
# connection = pymysql.connect(**db_config)
# example = """
# # {"input": "市盈率>0,市销率ps>-0.6", "query": "select * from financial WHERE pe_ttm > 0 AND ps > -0.6;"},
#
template_prompt = """
你是SQL专家。给定一个输入问题，创建一个语法正确的SQL语句查询来运行
以下是可能用到一些表的结构信息：
{table_info}



仔细审查SQL查询的初稿，找出SQL语句中查询中常见的错误，包括：
-使用BETWEEN进行独家范围
-谓词中的数据类型不匹配
-不要丢失或错误比较运算符（例如>、<、>=、<=、=）
-使用正确的列进行连接
在进行必要的更正后，提供优化且无错误的SQL查询作为最终输出。

Input: {question}
Output:
"""
# answer_prompt = [
#     ("system", "你是SQL专家。给定一个输入问题，创建一个语法正确的SQL语句查询来运行\n"
#                "以下是可能用到一些表的结构信息：{table_info}\n\n"
#                "仔细审查SQL查询的初稿，找出SQL语句中查询中常见的错误，包括：\n"
#                "-使用BETWEEN进行独家范围\n"
#                "-谓词中的数据类型不匹配\n"
#                "-不要丢失或错误比较运算符（例如>、<、>=、<=、=）\n"
#                "-使用正确的列进行连接\n"
#                "在进行必要的更正后，提供优化且无错误的SQL查询作为最终输出。\n\n"
#                "Input: {question}\n"
#                "Output:"),
# ]

# db = SQLDatabase.from_uri(
#     f"mysql+pymysql://{CONSTANT.DB_USER}:{CONSTANT.DB_PASSWORD}@{CONSTANT.DB_HOST}/{CONSTANT.DB_DATABASE}")


class StockInfo:
    def __init__(self, **kwargs):
        self._attributes = OrderedDict()
        # 假设数据库返回的列名与 stockInfo 的属性名相同
        for key, value in kwargs.items():
            self._attributes[key] = value

    def to_dict(self):
        return self._attributes.copy()


def convert_date(obj):
    """Convert datetime.date or datetime.datetime objects to ISO format."""
    if isinstance(obj, (datetime.date, datetime.datetime)):
        return obj.isoformat()
    return obj


class SQL_Query:
    def __init__(self, model):
        self.model = model
        # 创建提示词
        prompt = ChatPromptTemplate.from_messages(
            [("system", template_prompt)])
        setup = RunnableParallel({
            "table_info": RunnablePassthrough(),
            "question": RunnablePassthrough()})
        # prompt = ChatPromptTemplate.from_messages(answer_prompt)
        print("Answer Prompt:", prompt)
        self.prompt_ = prompt
        self.chain_ = prompt | model | setup

    def invoke(self, question: str, table_info):
        try:
            response = self.chain_.invoke({
                "question": question,
                "table_info": table_info
            })
            if False:
                prompt_string = self.prompt_.format(address=address)
                print(prompt_string)
            return response
        except Exception as e:
            print(f"query address exception:{e}")
            return None

    # def query(self, query_msg):
    #     chain = create_sql_query_chain(self.model, prompt=self.prompt)
    #     # 指定数据库表名字
    #     response = chain.invoke(SQLInputWithTables(question=query_msg, table_names_to_use=[CONSTANT.TABLE]))
    #     # print(chain.get_prompts()[0].pretty_print())
    #     # context = db.get_context()
    #     # prompt_with_context = chain.get_prompts()[0].partial(table_info=context["table_info"])
    #     # print(chain.get_prompts()[0])
    #     # full_chain = RunnablePassthrough.assign(table_names_to_use={"table_names_to_use": "financial"}) | chain
    #     # response = chain.invoke({"question": query_msg})
    #     # response = None
    #     print("================================")
    #     print(response)
    #     pattern = r"(?i)WHERE\s+.*?(?=LIMIT|\;)"
    #     # pattern = r"from.*"
    #     match = re.search(pattern, response, re.IGNORECASE)
    #     if match:
    #         where_condition = match.group(0)
    #         sql_condition = f"select * from {CONSTANT.TABLE} {where_condition};"
    #         print(sql_condition)
    #         try:
    #             with connection.cursor() as cursor:
    #                 # 执行查询
    #                 # sql = "YOUR SQL QUERY HERE"
    #                 cursor.execute(sql_condition)
    #
    #                 # 获取列名
    #                 column_names = [desc[0] for desc in cursor.description]
    #
    #                 # 获取查询结果
    #                 results = cursor.fetchall()
    #
    #                 # 将结果转换为字典列表
    #                 # dict_results = [dict(map(lambda item: (item[0], convert_date(item[1])), zip(column_names, row)))
    #                 #                 for row in results]/# 使用 DataObject 类和 to_dict 方法处理查询结果
    #                 dict_results = [StockInfo(**dict(zip(column_names, row))).to_dict() for row in results]
    #                 print("数据", dict_results)
    #                 return dict_results
    #
    #         except Exception as e:
    #             raise e

            # finally:
            #     connection.close()
        else:
            print("No WHERE clause found.")
            print("数据查询")


if __name__ == '__main__':
    import sys

    llm = create_model()
    sql_query = SQL_Query(llm)
    # sys.stdout.reconfigure(encoding='utf-8')
    # print(sql_query.prompt.format(input="市盈率>0,市销率ps>-0.6,",top_k=10,table_info="financial"))
    # context = db.get_context()
    # print(list(context))
    # print(context['table_info'])
    question = "总股本大于2亿"
    table_info = [
        '"backtest_results": [',
        '    ("strategy_id", "int", "策略代码"),',
        '    ("backtesting_time", "int", "回测次数"),',
        '    ("annualized_returns", "varchar(255)", "年化收益率"),',
        '    ("cumulative_earnings", "varchar(255)", "总收益率"),',
        '    ("maximum_drawdown", "varchar(255)", "最大回撤"),',
        '    ("start_date", "varchar(255)", "开始"),',
        '    ("end_date", "varchar(255)", "结束"),',
        '],',
        '"backtest_data": [',
        '    ("ts_code", "varchar(10)", "股票代码"),',
        '    ("trade_date", "varchar(20)", "交易日期"),',
        '    ("open", "double", "开盘价"),',
        '    ("high", "double", "最高价"),',
        '    ("low", "double", "最低价"),',
        '    ("close_x", "double", "收盘价"),',
        '    ("pre_close", "double", "前收价"),',
        '    ("change", "double", "涨跌额"),',
        '    ("pct_chg", "double", "涨跌幅"),',
        '    ("vol", "double", "成交量"),',
        '    ("amount", "double", "成交额"),',
        '    ("turnover_rate", "double", "换手率"),',
        '    ("turnover_rate_f", "double", "自由流通股换手率"),',
        '    ("volume_ratio", "double", "量比"),',
        '    ("pe", "double", "市盈率"),',
        '    ("pe_ttm", "double", "动态市盈率"),',
        '    ("pb", "double", "市净率"),',
        '    ("ps", "double", "市销率"),',
        '    ("ps_ttm", "double", "动态市销率"),',
        '    ("dv_ratio", "double", "股息率"),',
        '    ("dv_ttm", "double", "动态股息率"),',
        '    ("total_share", "double", "总股本"),',
        '    ("float_share", "double", "流通股本"),',
        '    ("free_share", "double", "自由流通股"),',
        '    ("total_mv", "double", "总市值（万元）"),',
        '    ("circ_mv", "double", "流通市值（万元）"),',
        '],'
    ]

    answer = sql_query.invoke(question=question, table_info=table_info)
    print(answer)
    # answer = sql_query.query("市销率ps>-0.6")
    # answer = sql_query.query("市盈率>0,市销率ps>-0.6")
    # print(answer)
    # class Table(BaseModel):
    #     """Table in SQL database."""
    #
    #     name: str = Field(description="Name of table in SQL database.")
    #
    #
    # table_names = "\n".join(db.get_usable_table_names())
    # system = f"""Return the names of ALL the SQL tables that MIGHT be relevant to the user question. \
    # The tables are:
    #
    # {table_names}
    #
    # Remember to include ALL POTENTIALLY RELEVANT tables, even if you're not sure that they're needed."""
    #
    # prompt = ChatPromptTemplate.from_messages(
    #     [
    #         ("system", system),
    #         ("human", "{input}"),
    #     ]
    # )
    # llm_with_tools = llm.bind_tools([Table])
    # output_parser = PydanticToolsParser(tools=[Table])
    #
    # table_chain = prompt | llm_with_tools | output_parser
    #
    # table_chain.invoke({"input": "市销率ps>-0.6"})
