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
from langchain_core.output_parsers.openai_tools import PydanticToolsParser
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.runnables import RunnablePassthrough

pymysql.install_as_MySQLdb()
db_config = {
    'host': CONSTANT.DB_HOST,
    'user': CONSTANT.DB_USER,
    'password': CONSTANT.DB_PASSWORD,
    'database': CONSTANT.DB_DATABASE,
}

connection = pymysql.connect(**db_config)
example = """
{"input": "市盈率>0,市销率ps>-0.6", "query": "select * from financial WHERE pe_ttm > 0 AND ps > -0.6;"},


"""
answer_prompt = """
      You are a {dialect} expert. Given an input question, create a syntactically correct {dialect} query to run.
      Unless the user specifies in the question a specific number of examples to obtain, query for at most {top_k} results using the LIMIT clause as per {dialect}.
      Pay attention to use date('now') function to get the current date, if the question involves "today".If the problem involves comparison operators (such as>,<,>=), please extract them correctly

      Here is the relevant table info:
      {table_info}
      Below are a number of examples of questions and their corresponding SQL queries:
      {example}

      Carefully review the preliminary draft of the query for common errors typically found in {dialect} queries, including:
      - Using NOT IN with NULL values
      - Using UNION when UNION ALL should have been used
      - Using BETWEEN for exclusive ranges
      - Data type mismatch in predicates
      - Ensuring the join columns are correct
      - Do not lose or mistake comparison operators (e.g. >,<,>=,<=,=)
      - Properly quoting identifiers
      - Using the correct number of arguments for functions
      - Casting to the correct data type
      - Using the proper columns for joins

      Upon making necessary corrections, provide an optimized and error-free SQL query as the final output.
      
          """

db = SQLDatabase.from_uri(
    f"mysql+pymysql://{CONSTANT.DB_USER}:{CONSTANT.DB_PASSWORD}@{CONSTANT.DB_HOST}/{CONSTANT.DB_DATABASE}")


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
        self.prompt = ChatPromptTemplate.from_messages(
            [("system", answer_prompt), ("human", "{input}")]).partial(dialect=db.dialect,example=example)

    def query(self, query_msg):
        chain = create_sql_query_chain(self.model, db, prompt=self.prompt)
        # 指定数据库表名字
        response = chain.invoke(SQLInputWithTables(question=query_msg, table_names_to_use=[CONSTANT.TABLE]))
        # print(chain.get_prompts()[0].pretty_print())
        # context = db.get_context()
        # prompt_with_context = chain.get_prompts()[0].partial(table_info=context["table_info"])
        # print(chain.get_prompts()[0])
        # full_chain = RunnablePassthrough.assign(table_names_to_use={"table_names_to_use": "financial"}) | chain
        # response = chain.invoke({"question": query_msg})
        # response = None
        print("================================")
        print(response)
        pattern = r"(?i)WHERE\s+.*?(?=LIMIT|\;)"
        # pattern = r"from.*"
        match = re.search(pattern, response, re.IGNORECASE)
        if match:
            where_condition = match.group(0)
            sql_condition = f"select * from {CONSTANT.TABLE} {where_condition};"
            print(sql_condition)
            try:
                with connection.cursor() as cursor:
                    # 执行查询
                    # sql = "YOUR SQL QUERY HERE"
                    cursor.execute(sql_condition)

                    # 获取列名
                    column_names = [desc[0] for desc in cursor.description]

                    # 获取查询结果
                    results = cursor.fetchall()

                    # 将结果转换为字典列表
                    # dict_results = [dict(map(lambda item: (item[0], convert_date(item[1])), zip(column_names, row)))
                    #                 for row in results]/# 使用 DataObject 类和 to_dict 方法处理查询结果
                    dict_results = [StockInfo(**dict(zip(column_names, row))).to_dict() for row in results]
                    print("数据",dict_results)
                    return dict_results

            except Exception as e:
                raise e

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
    context = db.get_context()
    # print(list(context))
    # print(context['table_info'])
    answer = sql_query.query("市销率ps>-0.6")
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
