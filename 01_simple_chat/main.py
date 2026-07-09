"""
最简单的 Agent：初始化 LLM Client → 接收用户输入 → 返回 LLM 回复
LLM Client 从 common 模块统一引入
"""

from common.llm import LLMClient


def main():
    # 1. 初始化 LLM Client
    llm = LLMClient()

    print("🤖 Agent 已启动！输入内容对话，输入 quit 退出\n")

    while True:
        user_input = input("你：")
        if user_input.lower() == "quit":
            print("再见！")
            break

        reply = llm.chat(user_input)
        print(f"Agent：{reply}\n")


if __name__ == "__main__":
    main()
