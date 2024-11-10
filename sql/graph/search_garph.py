from py2neo import Graph
import re


class SearchGraph:
    def __init__(self):
        # 连接到 Neo4j
        self.graph = Graph("bolt://localhost:7687", auth=("neo4j", "123456"))
        self.mapping = self.get_field_mapping()

    # 获取所有字段的映射
    def get_field_mapping(self):
        query = """
        MATCH (t:Table)-[:HAS_FIELD]->(f:Field)
        RETURN t.name AS table_name, f.name AS field_name, f.comment AS field_comment
        """
        results = self.graph.run(query).data()
        mapping = {}
        for result in results:
            # 只考虑非空的字段名称和注释
            if result['field_comment']:
                mapping[result['field_comment']] = f"{result['table_name']}.{result['field_name']}"
            if result['field_name']:
                mapping[result['field_name']] = f"{result['table_name']}.{result['field_name']}"

        return mapping

    # 替换字段函数
    def replace_fields(self, query):
        # 按照字段名的长度降序排序，确保长的字段优先匹配
        sorted_fields = sorted(self.mapping.keys(), key=len, reverse=True)
        for field in sorted_fields:
            # 尝试使用简单的匹配，避免 \b
            # print(f"尝试替换字段: {field}")
            # if re.search(r'\s*' + re.escape(field) + r'\s*', query):
            query = re.sub(r'\s*' + re.escape(field) + r'\s*', lambda m: f" {self.mapping[field]} ", query)
            # print(f"替换后文本: {query}")  # 打印每次替换后的文本
            # break  # 找到替换后退出循环
        return query.strip()



if __name__=="__main__":
    search = SearchGraph()
    query_text = "市盈率TTM大于2亿,市销率小于0.6的股票"
    response = search.replace_fields(query_text)


    # 示例输入
    # replaced_query = replace_fields(query_text, field_mapping)

    print(response)  # 输出: backtest_data.total_share大于2亿的股票
