"""
RAG Agent 入口
运行方式：uv run python 04_rag/main.py

效果：加载知识库文档 → 交互式问答（基于文档回答）
"""

import os
from vector_store import VectorStore
from rag_agent import RAGAgent


KNOWLEDGE_FILE = os.path.join(os.path.dirname(__file__), "knowledge_base.txt")


def main():
    # ① 加载知识库文档
    print("=" * 50)
    print("📚 加载知识库...")
    print("=" * 50)

    with open(KNOWLEDGE_FILE, "r", encoding="utf-8") as f:
        text = f.read()

    # ② 初始化向量库，添加文档（自动切片 + 向量化）
    store = VectorStore()
    store.add_document(text)

    # ③ 创建 RAG Agent
    agent = RAGAgent(store, top_k=3)

    # ④ 交互式问答
    print("\n" + "=" * 50)
    print("🤖 RAG Agent 已启动！输入问题基于文档回答，输入 quit 退出")
    print("   试试问：暗影迷宫怎么打？/ 宠物怎么进化？/ 公会战什么时候开？")
    print("=" * 50)

    while True:
        question = input("\n你：")
        if question.lower() == "quit":
            print("再见！")
            break

        answer = agent.ask(question)
        print(f"\nAgent：{answer}")


if __name__ == "__main__":
    main()
