"""
练习目标：生成器表达式（Generator Expression）+ 惰性求值

AI 应用场景：
    - 处理大向量库（百万级 chunk）：不能一次性 load 进内存
    - 流式处理数据集：读一行、处理一行、输出一行

核心语法：
    (x for x in data)     → 生成器表达式，惰性计算，不占内存
    [x for x in data]     → 列表推导式，立即全部计算，占内存

对比：
    列表推导 [x for x in range(1_000_000)]  → 内存占用 ~40MB
    生成器    (x for x in range(1_000_000)) → 内存占用 ~0，用到才算
"""

import sys
from typing import Iterable


def lazy_chunks(file_path: str) -> Iterable[str]:
    """处理大文件的正确姿势：yield 一次处理一行"""
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            yield line.strip()  # 一次只读一行，超省内存


if __name__ == "__main__":
    print("【对比 1】内存占用")
    big_range = range(100_000_000)

    list_comp = [x * x for x in big_range]      # ❌ 直接爆内存（不要真跑这行！）
    # 实际用生成器对比就够了：
    gen = (x * x for x in big_range)            # ✅ 几乎不占内存

    print(f"  列表推导式占用: {sys.getsizeof([x for x in range(1000)])} 字节 / 1000 个元素")
    print(f"  生成器表达式占用: {sys.getsizeof(gen)} 字节（不管数据多大）")

    print("\n【对比 2】惰性求值：只取前 5 个，后面的根本不算")
    gen2 = (x * x for x in range(10_000_000) if x % 2 == 0)
    for i, val in enumerate(gen2):
        if i >= 5:
            break
        print(f"  第 {i+1} 个偶数平方: {val}")

    print("\n【对比 3】处理大文件（AI 数据处理的常见写法）")
    # 不把整个文件读进来，一次读一行处理
    chunks = lazy_chunks("../../04_rag/knowledge_base.txt")
    for i, line in enumerate(chunks):
        if i >= 3:
            print("  ...（后面的行按需继续读，不占内存）")
            break
        print(f"  第 {i+1} 行: {line[:40]}...")

    print("""
💡 一句话总结：
    - 列表推导式：先付钱后吃饭（内存立即占用）
    - 生成器表达式：吃一口付一口（惰性计算）
    - Agent 项目里处理海量 chunk 时必须用生成器
""")
