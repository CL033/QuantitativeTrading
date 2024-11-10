import os
import faiss
from langchain_community.embeddings.dashscope import DashScopeEmbeddings
from langchain_core.embeddings import Embeddings
from langchain.docstore.document import Document
from langchain_community.vectorstores.faiss import FAISS
from typing import List, Optional
from collections import OrderedDict
from vector_stores.sql_txt_loader import SQLTxtLoader
import hashlib
from langchain_core.vectorstores import VectorStore


class FaissStore:
    def __init__(self, name: str, data_path: str, embeddings: Embeddings):
        print("初始化向量库：", name)
        self._name = name
        self._data_path = data_path
        self._docs: List[Document] = []
        if data_path:
            loader = SQLTxtLoader(data_path)
            self._docs: List[Document] = loader.load_tables_info()
        self._vector_store, _already_exist = self._init_vector_store(name, data_path, embeddings)
        if self._docs and not _already_exist:
            unique_docs_ordered = list(OrderedDict((doc.page_content, doc) for doc in self._docs).values())
            self._docs = unique_docs_ordered
            self._vector_store.add_documents(self._docs,
                                             ids=[FaissStore._encode_document(doc) for doc in self._docs])
        self._post_vector_store(self._vector_store, self._name, embeddings)

    def _init_vector_store(self, name: str, data_path: str, embeddings: Embeddings):
        vector_store = self._restore_vectorstore(name, embeddings)
        _already_exist = True
        if vector_store:
            return vector_store, _already_exist
        else:
            _already_exist = False
            return FAISS.from_texts(texts=[""], embedding=embeddings), _already_exist

    def _encode_document(doc: Document) -> str:
        return hashlib.md5(doc.page_content.encode("utf-8")).hexdigest()

    def _post_vector_store(self, vector_store: VectorStore, name: str, embeddings: Embeddings):
        self._serialize_vectorstore(vector_store, name, embeddings)

    def _serialize_vectorstore(self, vector_store: VectorStore, name: str, embeddings: Embeddings):
        md5_file_name = self._cache_file_name(name, embeddings)

        faiss_index_file_path = self._faiss_index_file_name(md5_file_name)
        faiss_index_bytes = self._vector_store.serialize_to_bytes()
        with open(faiss_index_file_path, "wb") as f:
            f.write(faiss_index_bytes)

    def _cache_file_name(self, name: str, embeddings: Embeddings):
        file_name = name + str(type(embeddings))
        md5_file_name = hashlib.md5(file_name.encode("utf-8")).hexdigest()
        return md5_file_name

    def _faiss_index_file_name(self, file_name: str):
        return os.path.join(os.path.dirname(__file__), 'vector_stores/caches/') + (file_name + "_faiss_index.faiss")

    def _restore_vectorstore(self, name: str, embeddings: Embeddings) -> Optional[VectorStore]:
        md5_file_name = self._cache_file_name(name, embeddings)

        faiss_index_file_path = self._faiss_index_file_name(md5_file_name)

        if not os.path.exists(faiss_index_file_path):
            return False

        faiss_index = None
        with open(faiss_index_file_path, "rb") as f:
            faiss_index = f.read()

        vector_store: VectorStore = FAISS.deserialize_from_bytes(faiss_index, embeddings)
        return vector_store

    def vector_store(self) -> VectorStore:
        return self._vector_store
