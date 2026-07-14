"""
RAG Agent：检索增强生成

流程：
    用户提问 → 从向量库检索相关段落 → 段落 + 问题一起发给 LLM → LLM 基于段落回答

和之前 Agent 的区别：
    ReAct / Function Calling：调工具获取外部信息
    RAG：从知识库检索相关信息，增强 LLM 的回答
"""

import os
from dotenv import load_dotenv
from openai import OpenAI
from typing import Optional
from vector_store import VectorStore

load_dotenv()


class RAGAgent:
    """
    RAG Agent：检索 + 生成

    用法：
        agent = RAGAgent(vector_store)
        answer = agent.ask("报销流程是什么？")
    """

    # RAG 的 Prompt 模板：告诉 LLM "只能基于提供的资料回答"
    SYSTEM_PROMPT = """你是一个问答助手。请基于以下参考资料回答用户的问题。

要求：
1. 只能基于参考资料回答，不要编造信息
2. 如果参考资料中没有相关内容，请明确说"根据已有资料，我无法回答这个问题"
3. 回答要简洁准确，可以适当引用资料原文

参考资料：
{context}
"""

    def __init__(self, vector_store: VectorStore, top_k: int = 3):
        """
        Args:
            vector_store: 向量库（已经添加了文档）
            top_k: 每次检索返回几段
        """
        self.vector_store = vector_store
        self.top_k = top_k
        self.client = OpenAI(
            api_key=os.getenv("LLM_API_KEY"),
            base_url=os.getenv("LLM_BASE_URL"),
        )
        self.model = os.getenv("LLM_MODEL")

    def ask(self, question: str) -> str:
        """
        回答用户问题

        流程：
            ① 检索：从向量库找相关段落
            ② 生成：把段落 + 问题发给 LLM
        """
        # ① 检索相关段落
        print(f"\n🔍 检索中...")
        results = self.vector_store.search(question, top_k=self.top_k)

        if not results:
            return "知识库为空，无法回答。"

        # 展示检索结果
        context_parts = []
        for i, (chunk, score) in enumerate(results):
            print(f"   [{i+1}] 相似度: {score:.4f} | {chunk[:50]}...")
            context_parts.append(chunk)

        context = "\n\n".join(context_parts)

        # ② 构建 Prompt，把检索到的资料塞进去
        system_prompt = self.SYSTEM_PROMPT.format(context=context)
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question},
        ]

        # ③ 调用 LLM 生成回答
        print(f"\n🧠 生成回答中...")
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0,  # RAG 用低温度，保证回答准确
        )

        return response.choices[0].message.content


if __name__ == "__main__":
    # 快速测试
    store = VectorStore()
    with open("knowledge_base.txt", "r", encoding="utf-8") as f:
        store.add_document(f.read())

    agent = RAGAgent(store)
    answer = agent.ask("年假有几天？")
    print(f"\n回答: {answer}")
