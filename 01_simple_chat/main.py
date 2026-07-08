"""
最简单的 Agent：初始化 LLM Client → 接收用户输入 → 返回 LLM 回复
配置从 .env 文件读取，API Key 不会暴露在代码中
"""

from dotenv import load_dotenv
from openai import OpenAI
import os

# 加载 .env 配置文件（从项目根目录运行时可直接找到）
load_dotenv()


# 1. 初始化 LLM Client（从环境变量读取配置）
client = OpenAI(
    base_url=os.getenv("DEEPSEEK_BASE_URL"),
    api_key=os.getenv("DEEPSEEK_API_KEY"),
)

# 从环境变量读取模型名称
MODEL = os.getenv("DEEPSEEK_MODEL")


def chat(user_input: str) -> str:
    """发送用户消息给 LLM，返回回复"""
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "你是一个有帮助的助手。"},
            {"role": "user", "content": user_input},
        ],
    )
    # 从回复中提取文本内容
    return response.choices[0].message.content


def main():
    print("🤖 Agent 已启动！输入内容对话，输入 quit 退出\n")

    while True:
        user_input = input("你：")
        if user_input.lower() == "quit":
            print("再见！")
            break

        reply = chat(user_input)
        print(f"Agent：{reply}\n")


if __name__ == "__main__":
    main()
