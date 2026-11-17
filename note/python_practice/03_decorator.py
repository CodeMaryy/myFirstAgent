"""
练习目标：装饰器 @decorator

AI 应用场景：
    - 统计每个 LLM 调用耗时（不想改原函数代码）
    - 给工具函数自动加"重试"逻辑
    - FastAPI 的 @app.get("/") 就是装饰器

核心语法：
    @decorator_name    → 把下面的函数"包装"一下再定义
    wrapper(*args, **kwargs) → 能接住任意参数，转发给原函数
    @functools.wraps(func)     → 保留原函数的名字和文档字符串
"""

import functools
import time
from typing import Callable


def log_time(func: Callable) -> Callable:
    """装饰器：打印函数执行耗时"""
    @functools.wraps(func)  # 不加这个，wrapper 会"覆盖"原函数的名字
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)  # 调用原函数
        elapsed = time.time() - start
        print(f"⏱️  函数 {func.__name__} 执行耗时: {elapsed:.2f}s")
        return result
    return wrapper


def retry(max_attempts: int = 3) -> Callable:
    """带参数的装饰器：失败自动重试（AI 调用常用）"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    print(f"  第 {attempt} 次失败: {e}")
                    if attempt == max_attempts:
                        raise
        return wrapper
    return decorator


# ---------- 使用 ----------
@log_time
def call_llm_model() -> str:
    """模拟一次 LLM 调用"""
    time.sleep(0.3)
    return "模型回复内容"


@retry(max_attempts=3)
def unstable_api() -> str:
    """模拟一个偶尔失败的 API"""
    if time.time() % 1 > 0.5:  # 随机失败
        raise ConnectionError("网络波动")
    return "成功"


if __name__ == "__main__":
    print("【例子 1】统计耗时")
    result = call_llm_model()
    print(f"  结果: {result}")
    print(f"  函数名: {call_llm_model.__name__}（functools.wraps 保留了原名）\n")

    print("【例子 2】失败重试")
    try:
        print(f"  结果: {unstable_api()}")
    except Exception as e:
        print(f"  最终失败: {e}")

    print("""
💡 装饰器的本质：
    @log_time 写在 def 上面 = python 自动帮你执行了
    call_llm_model = log_time(call_llm_model)
    原函数一行没改，但多了一层"包装"
""")
