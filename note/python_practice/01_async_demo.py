"""
练习目标：async / await 并发

AI 应用场景：
    - 同时调用多个 LLM（比如 3 路模型投票）
    - 同时搜索多个数据源（天气 + 新闻 + 数据库）
    - 不用串行等待，总耗时 ≈ 最慢那一次

核心语法：
    async def  → 声明一个"协程函数"（定义时不会立刻执行）
    await      → 在协程里"挂起等待"，但不阻塞其他协程
    asyncio.gather() → 把多个协程"一起扔出去"并发执行
    asyncio.run()    → 启动整个事件循环
"""

import asyncio
import time


async def call_api(name: str, delay: float) -> str:
    """模拟一次 API 调用，耗时 delay 秒"""
    print(f"  {name} 开始调用...")
    await asyncio.sleep(delay)  # 模拟网络等待（挂起，不占 CPU）
    return f"{name} 的结果"


async def main():
    print("【串行执行】一次等一个")
    start = time.time()
    await call_api("串行-1", 0.5)
    await call_api("串行-2", 0.5)
    await call_api("串行-3", 0.5)
    serial_time = time.time() - start
    print(f"  → 串行总耗时: {serial_time:.2f}s\n")

    print("【并发执行】三个同时发出去")
    start = time.time()
    results = await asyncio.gather(
        call_api("并发-1", 0.5),
        call_api("并发-2", 0.5),
        call_api("并发-3", 0.5),
    )
    concurrent_time = time.time() - start
    print(f"  → 并发总耗时: {concurrent_time:.2f}s")
    print(f"  → 返回结果: {results}")

    print(f"\n💡 节省了 {serial_time - concurrent_time:.2f}s（串行是并发的 {serial_time/concurrent_time:.1f} 倍）")


if __name__ == "__main__":
    # asyncio.run 是 Python 3.7+ 的固定入口写法
    asyncio.run(main())
