"""
Function Calling Agent
运行方式：uv run python 03_function_calling/main.py

和 ReAct 版本的核心区别：
    ReAct：           Prompt 约束格式 → LLM 返回纯文本 → 正则解析
    Function Calling： tools 参数声明 → LLM 返回结构化 JSON → 直接用

不需要 Prompt 模板，不需要正则解析，SDK 帮你搞定一切。
"""

import json
from dotenv import load_dotenv
from openai import OpenAI
import os

from common.llm import LLMClient
from tools import create_default_tools

load_dotenv()


def run_agent(question: str, max_steps: int = 5):
    """
    Function Calling Agent 的核心循环

    流程：
        1. 把问题发给 LLM，同时告诉它有哪些工具可用
        2. LLM 决定：直接回答 or 调用工具
        3. 如果调用工具 → 执行工具 → 把结果喂回 LLM → 回到 1
        4. 如果直接回答 → 结束
    """
    llm = OpenAI(
        api_key=os.getenv("LLM_API_KEY"),
        base_url=os.getenv("LLM_BASE_URL"),
    )
    model = os.getenv("LLM_MODEL")
    tools = create_default_tools()

    # messages 列表：记录整个对话历史（LLM 靠它理解上下文）
    messages = [
        {"role": "system", "content": "你是一个有帮助的助手，可以调用工具来回答问题。"},
        {"role": "user", "content": question},
    ]

    print(f"\n🤖 开始处理问题: {question}")

    for step in range(1, max_steps + 1):
        print(f"\n{'='*50}")
        print(f"📍 第 {step} 步")
        print(f"{'='*50}")

        # ① 调用 LLM，把工具声明通过 tools 参数传进去
        response = llm.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools.get_schemas(),      # ← 关键：传工具声明
            temperature=0,
        )

        msg = response.choices[0].message

        # ② 检查 LLM 是否要调用工具
        if msg.tool_calls:
            # 把 LLM 的回复加入历史
            messages.append(msg)

            # ③ 遍历所有工具调用（LLM 可能一次调多个）
            for tool_call in msg.tool_calls:
                func_name = tool_call.function.name
                # ← 关键区别：参数是结构化 JSON，不用正则解析！
                func_args = json.loads(tool_call.function.arguments)

                print(f"\n🎬 调用工具: {func_name}({func_args})")

                # ④ 执行工具
                result = tools.execute(func_name, func_args)
                print(f"👀 结果: {result}")

                # ⑤ 把工具结果喂回 LLM
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result,
                })

            # 继续循环，让 LLM 看到工具结果后决定下一步
            continue

        # ⑥ LLM 没有调用工具，说明它已经有答案了
        print(f"\n🎉 最终答案: {msg.content}")
        return msg.content

    print(f"\n⚠️ 已达到最大步数 {max_steps}")
    return "抱歉，无法在限定步数内完成。"


if __name__ == "__main__":
    question = "北京和上海今天的温度差是多少？"
    answer = run_agent(question)

    print(f"\n{'='*50}")
    print(f"📊 问题: {question}")
    print(f"📊 回答: {answer}")
    print(f"{'='*50}")
