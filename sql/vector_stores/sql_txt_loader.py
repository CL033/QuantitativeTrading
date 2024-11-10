from pathlib import Path
import re
from typing import Dict, List, Optional
from langchain.docstore.document import Document
from langchain.document_loaders import TextLoader
import os

from sql.graph.create_graph import GraphDatabaseHandler


class SQLTxtLoader:
    """将TXT文件里面的内容加载到文档列表之中."""

    def __init__(self, directory_path: str):
        self.directory_path = directory_path
        self.tables_info = {}

    def sql_txt_load(self) -> List[Document]:
        documents = []
        # 遍历目录下的所有文件
        for filename in os.listdir(self.directory_path):
            if filename.endswith('.txt'):
                file_path = os.path.join(self.directory_path, filename)
                loader = TextLoader(file_path, encoding='utf-8')
                documents.extend(loader.load())  # 加载并添加到文档列表中
        return documents

    def load_tables_info(self):
        """
        遍历文件夹下的所有 sql 表结构文档
        """
        for filename in os.listdir(self.directory_path):
            if filename.endswith('.txt'):
                file_path = os.path.join(self.directory_path, filename)
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    self._parse_table_info(content)

        documents = self.create_documents()
        return documents

    def _parse_table_info(self, sql_content):
        """
        对表结构的格式进行转化，匹配表名和字段信息
        格式如下：
        self.tables_info = {
            "table": [
                ("column", "type", "comment"),
                ...
            ],
        """
        # 使用正则表达式匹配表名和字段信息
        table_name_match = re.search(r'CREATE TABLE `(\w+)`', sql_content)
        if table_name_match:
            table_name = table_name_match.group(1)
            fields_info = []

            # 匹配字段及其属性的模式
            field_pattern = r'`(\w+)` (\w+\(?\d*\)?)(?: CHARACTER SET [^ ]+ COLLATE [^ ]+)? DEFAULT NULL COMMENT \'([^\']+)\''
            for match in re.finditer(field_pattern, sql_content):
                field_name = match.group(1)
                field_type = match.group(2)
                comment = match.group(3)
                fields_info.append((field_name, field_type, comment))

            self.tables_info[table_name] = fields_info

    def create_documents(self):
        documents = []
        for table_name, fields in self.tables_info.items():
            # 直接使用现有结构创建 Document 实例
            content = f'"{table_name}": [\n'
            for field_name, field_type, comment in fields:
                content += f'    ("{field_name}", "{field_type}", "{comment}"),\n'
            content += '],'
            documents.append(Document(page_content=content))
        return documents

    def get_tables_info(self):
        return self.tables_info


if __name__ == '__main__':
    current_dir = Path(
        os.path.abspath(__file__)).parent.parent.parent / 'query' / 'util' / 'train_data' / 'indu_table_creates'

    loader = SQLTxtLoader(str(current_dir))
    document = loader.load_tables_info()

    # 打印提取的表信息
    tables_info = loader.get_tables_info()

    print(document)
    # 创建图数据库
    graph_db = GraphDatabaseHandler("bolt://localhost:7687", "neo4j", "123456")
    graph_db.create_table_node(document)
    graph_db.close()
    # for table, fields in tables_info.items():
    #     print(f"表名: {table}")
    #     for field in fields:
    #         print(f"字段: {field[0]}, 类型: {field[1]}, 注释: {field[2]}")
