from neo4j import GraphDatabase
import json
import ast
import util.constant as CONSTANT
class GraphDatabaseHandler:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def create_table_node(self, documents):
        with self.driver.session() as session:
            for document in documents:
                content = document.page_content
                session.write_transaction(self._create_node, content)

    @staticmethod
    def parse_document_content(content):
        # 解析文档内容并返回表名和字段
        content = content.replace('(', '[').replace(')', ']')  # 将元组转换为列表
        data = json.loads(content)
        for table_name, fields in data.items():
            parsed_fields = []
            for field in fields:
                field_name, field_type, comment = field
                parsed_fields.append((field_name, field_type, comment))
            return table_name, parsed_fields

    @staticmethod
    def _create_node(tx, content):
        # content = content.replace('(', '[').replace(')', ']')  # 将元组转换为列表
        # data = ast.literal_eval(content)  # 使用 ast.literal_eval 解析为 Python 数据结构
        content = f"{{ {content.strip()} }}"  # 添加花括号并去除多余空白
        content = content.replace('(', '[').replace(')', ']')  # 将元组转换为列表

        try:
            data = ast.literal_eval(content)  # 使用 ast.literal_eval 解析为 Python 数据结构
        except SyntaxError as e:
            print(f"Syntax error: {e}")
            return

        # 创建表节点
        # tx.run(f"CREATE (t:Table {{name: '{table_name}'}})")
        for table_name, fields in data.items():
            # 创建表节点
            tx.run(f"CREATE (t:Table {{name: '{table_name}'}})")
            for field in fields:
                field_name, field_type, comment = field
                # 为字段创建属性
                tx.run(f"""
                            MATCH (t:Table {{name: '{table_name}'}})
                            CREATE (f:Field {{name: '{field_name}', type: '{field_type}', comment: '{comment}'}})
                            CREATE (t)-[:HAS_FIELD]->(f)
                        """)


# 连接到图数据库
graph_db = GraphDatabaseHandler(CONSTANT.NEO4J_HOST, CONSTANT.NEO4J_USERNAME, CONSTANT.NEO4J_PASSWORD)

# 表结构
table_name = "backtest_data"
fields = [
    ("id", "int", "主键"),
    ("ts_code", "varchar(10)", "股票代码"),
    ("trade_date", "varchar(20)", "交易日期"),
    ("open", "double", "开盘价"),
    ("high", "double", "最高价"),
    ("low", "double", "最低价"),
    ("close_x", "double", "收盘价"),
    ("pre_close", "double", "前收价"),
    ("change", "double", "涨跌额"),
    ("pct_chg", "double", "涨跌幅"),
    ("vol", "double", "成交量"),
    ("amount", "double", "成交额"),
    ("close_y", "double", ""),
    ("turnover_rate", "double", "换手率"),
    ("turnover_rate_f", "double", "自由流通股换手率"),
    ("volume_ratio", "double", "量比"),
    ("pe", "double", "市盈率"),
    ("pe_ttm", "double", "动态市盈率"),
    ("pb", "double", "市净率"),
    ("ps", "double", "市销率"),
    ("ps_ttm", "double", "动态市销率"),
    ("dv_ratio", "double", "股息率"),
    ("dv_ttm", "double", "动态股息率"),
    ("total_share", "double", "总股本"),
    ("float_share", "double", "流通股本"),
    ("free_share", "double", "自由流通股"),
    ("total_mv", "double", "总市值（万元）"),
    ("circ_mv", "double", "流通市值（万元）"),
    ("year", "double", ""),
    ("pcf_ttm", "double", ""),
]

# 创建节点
# graph_db.create_table_node()

# 关闭连接
# graph_db.close()
