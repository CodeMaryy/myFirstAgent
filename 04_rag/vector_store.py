"""
向量存储模块：文本切片 + 向量化 + 相似度检索

RAG 的核心组件：
    1. 把文档切成小段（chunking）
    2. 每段文本转成向量（embedding）
    3. 查询时，把问题也转成向量，找最相似的几段
"""

import os
import json
import numpy as np
from dotenv import load_dotenv
from openai import OpenAI
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict, Tuple

load_dotenv()


class VectorStore:
    """
    向量存储：管理文档切片和向量检索

    用法：
        store = VectorStore()
        store.add_document("文档内容...")     # 添加文档（自动切片+向量化）
        results = store.search("问题", top_k=3) # 检索最相关的3段
    """

    def __init__(self):
        # Embedding 用阿里的 DashScope（兼容 OpenAI 协议）
        self.client = OpenAI(
            api_key=os.getenv("EMBED_API_KEY"),
            base_url=os.getenv("EMBED_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1"),
        )
        self.embedding_model = os.getenv("EMBED_MODEL_NAME", "text-embedding-v4")

        # 存储所有切片和对应的向量
        self.chunks: List[str] = []           # 文本切片
        self.vectors: List[np.ndarray] = []   # 对应的向量

    def _get_embedding(self, text: str) -> np.ndarray:
        """调用 API 把文本转成向量"""
        response = self.client.embeddings.create(
            model=self.embedding_model,
            input=text,
        )
        return np.array(response.data[0].embedding)

    def _split_text(self, text: str, chunk_size: int = 200, overlap: int = 50) -> List[str]:
        """
        把长文本切成小段

        Args:
            text:       原始文本
            chunk_size: 每段大约多少字符
            overlap:    相邻段重叠多少字符（保证上下文连贯）

        为什么要切片？
            - LLM 上下文有限，不能把整篇文档塞进去
            - 检索时只需要最相关的几段，不需要全文
        """
        chunks = []
        start = 0
        while start < len(text):
            # 找到切片结束位置
            end = start + chunk_size

            # 尽量在句号、换行处切，避免切断句子
            if end < len(text):
                for sep in ["\n\n", "\n", "。", "；", ".", ";"]:
                    pos = text.rfind(sep, start, end)
                    if pos > start:
                        end = pos + 1
                        break

            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)

            # 下一段从 end - overlap 开始，保证重叠
            start = end - overlap if end < len(text) else end

        return chunks

    def add_document(self, text: str, chunk_size: int = 200, overlap: int = 50):
        """
        添加文档到向量库
        自动完成：切片 → 向量化 → 存储
        """
        print(f"📄 文档总长度: {len(text)} 字符")

        # ① 切片
        chunks = self._split_text(text, chunk_size, overlap)
        print(f"✂️  切成 {len(chunks)} 段")

        # ② 逐段向量化
        for i, chunk in enumerate(chunks):
            vector = self._get_embedding(chunk)
            self.chunks.append(chunk)
            self.vectors.append(vector)
            if (i + 1) % 5 == 0:
                print(f"   已向量化 {i + 1}/{len(chunks)} 段")

        print(f"✅ 全部完成，向量库共 {len(self.chunks)} 段")

    def search(self, query: str, top_k: int = 3) -> List[Tuple[str, float]]:
        """
        检索：找和 query 最相似的 top_k 段

        Args:
            query: 用户的问题
            top_k: 返回最相似的几段

        Returns:
            [(文本, 相似度分数), ...] 按相似度从高到低排序
        """
        if not self.chunks:
            return []

        # ① 把问题转成向量
        query_vector = self._get_embedding(query).reshape(1, -1)

        # ② 把所有文档向量拼成矩阵
        doc_vectors = np.array(self.vectors)

        # ③ 计算问题和每段文档的余弦相似度
        similarities = cosine_similarity(query_vector, doc_vectors)[0]

        # ④ 取相似度最高的 top_k 段
        top_indices = np.argsort(similarities)[-top_k:][::-1]

        results = []
        for idx in top_indices:
            results.append((self.chunks[idx], float(similarities[idx])))

        return results


if __name__ == "__main__":
    # 测试
    store = VectorStore()

    with open("knowledge_base.txt", "r", encoding="utf-8") as f:
        text = f.read()

    store.add_document(text)

    print("\n--- 测试检索 ---")
    query = "报销流程是什么？"
    results = store.search(query, top_k=2)

    for i, (chunk, score) in enumerate(results):
        print(f"\n[{i+1}] 相似度: {score:.4f}")
        print(f"内容: {chunk[:100]}...")
