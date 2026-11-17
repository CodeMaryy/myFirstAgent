"""
练习目标：yield 生成器

AI 应用场景：
    - LLM 流式输出：ChatGPT 的"一个字一个字往外蹦"就是 yield
    - 读取大文件/大向量库：一次取一点，不把内存撑爆

核心语法：
    yield       → "暂停并吐出一个值"，函数状态被冻结，下次从暂停处继续
    for token in gen  → 每次只取一个值，用多少取多少

对比：
    普通函数 + return  → 一次性算完返回整个列表（等得久，占内存）
    生成器 + yield     → 惰性产出，用到才算、算到哪取到哪
"""

from typing import Generator


def fake_llm_stream(text: str) -> Generator[str, None, None]:
    """
    模拟 LLM 流式返回：每次 yield 一个词

    类型注解解读：
        Generator[返回值类型, 接收值类型, 最终返回值类型]
        这里：每次产出一个 str，不接收外部传入，结束时返回 None
    """
    for token in text.split(" "):
        yield token  # 生成器标志：暂停，交出控制权，调用方拿到这个值


def stream_print(gen: Generator[str, None, None]) -> None:
    """打印流式输出，模拟打字机效果"""
    print("🤖 LLM: ", end="", flush=True)
    for token in gen:
        print(token, end=" ", flush=True)  # 拿到一个打印一个，不用等全部完成
    print()  # 换行


if __name__ == "__main__":
    print("【方式一】流式输出（用户马上看到第一个字）")
    stream_print(fake_llm_stream("你好，我是流式输出的 LLM，一个字一个字返回"))

    print("\n【方式二】直接用列表（必须等函数全部执行完）")
    tokens = list(fake_llm_stream("一次性返回所有内容"))
    print(f"拿到的列表: {tokens}")

    print("""
💡 关键区别：
    - 流式：第一个 token 产出后立刻展示，其余的还在生成 → 体验好
    - 列表：必须全部生成完才能开始展示 → 用户干等
    - 后续 OpenAI API 的 stream=True 用的就是 yield
""")
