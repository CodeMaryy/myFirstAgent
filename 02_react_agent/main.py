"""
ReAct Agent 入口文件
运行方式：uv run python 02_react_agent/main.py
"""

from llm import LLMClient
from tools import ToolRegistry, calculator, fake_search
from react_agent import ReActAgent


def main():
    # 1. 初始化 LLM Client
    llm = LLMClient()

    # 2. 初始化工具注册器，注册工具
    registry = ToolRegistry()
    registry.register(
        "Calculator",
        "数学计算器，输入数学表达式（如 2+3*4）返回计算结果",
        calculator,
    )
    registry.register(
        "Search",
        "搜索引擎，搜索实时信息（如天气、新闻等）",
        fake_search,
    )

    # 3. 创建 ReAct Agent
    agent = ReActAgent(llm=llm, tools=registry, max_steps=5)

    # 4. 运行！
    # 试试这个需要多步推理 + 工具调用的问题
    question = "北京和上海今天的温度差是多少？"
    answer = agent.run(question)

    print(f"\n{'='*50}")
    print(f"📊 问题: {question}")
    print(f"📊 回答: {answer}")
    print(f"{'='*50}")


if __name__ == "__main__":
    main()
