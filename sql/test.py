from pathlib import Path
from langchain_community.embeddings.dashscope import DashScopeEmbeddings
import os

from sql.faiss_vector_store import FaissStore



os.environ["DASHSCOPE_API_KEY"] = ""


dashscopeEmbeddings = DashScopeEmbeddings(model="text-embedding-v2")

os.environ["VECTOR_STORE_TYPE"] = "FAISS"
file_name = "indu_table_creates"
data_abs_path = Path(os.path.abspath(__file__)).parent.parent / 'query' / 'util' / 'train_data' / 'indu_table_creates'
print(data_abs_path)

store = FaissStore(file_name, str(data_abs_path), dashscopeEmbeddings)


# 准备查询文本
query_text = "backtest_data. backtest_data.pe TTM大于2亿, backtest_data. backtest_data.ps 小于0.6的股票"
k = 5  # 获取更多结果
similar_docs = store.vector_store().similarity_search(query_text, k)
print(type(similar_docs))
# 打印所有相似文档的内容
for doc in similar_docs:
    print(doc.page_content)


