"""
练习目标：Pydantic 数据校验

AI 应用场景：
    - 定义 LLM 工具（tool/function calling）的参数结构
    - 结构化输出（Structured Output）：要求模型返回严格 JSON
    （OpenAI 官方 SDK 内部就是用 Pydantic 做参数校验的）

核心语法：
    class Xxx(BaseModel)   → 定义一个"数据模型"
    Field(ge=, le=, description=) → 字段约束 + 给 LLM 看的描述
    model_dump()           → 转成普通 dict，可以喂给 API
    类型不对            → 自动报错，不用自己写一堆 if
"""

from pydantic import BaseModel, Field, ValidationError


class WeatherTool(BaseModel):
    """天气查询工具的参数定义（模拟 function calling 的 JSON Schema）"""

    city: str = Field(description="城市名称，例如：北京")
    days: int = Field(default=1, ge=1, le=7, description="查询天数，1~7")
    unit: str = Field(default="celsius", description="温度单位：celsius 或 fahrenheit")


class SearchResult(BaseModel):
    """结构化输出的模型定义：让 LLM 必须返回这个格式"""

    answer: str = Field(description="回答内容")
    confidence: float = Field(ge=0.0, le=1.0, description="置信度 0~1")
    sources: list[str] = Field(description="引用来源列表")


if __name__ == "__main__":
    print("【例子 1】正确用法：自动类型转换 + 校验")
    tool = WeatherTool(city="上海", days=3)
    print(f"  模型对象: {tool}")
    print(f"  转成 dict: {tool.model_dump()}")

    print("\n【例子 2】自动校验：超出范围直接报错")
    try:
        bad = WeatherTool(city="北京", days=99)  # days 最大 7
    except ValidationError as e:
        print(f"  ✅ Pydantic 拦截: days 超出范围")
        print(f"  错误信息: {e.errors()[0]['msg']}")

    print("\n【例子 3】结构化输出：LLM 必须遵守这个格式")
    result = SearchResult(
        answer="报销需要先在 OA 系统提交申请，审批通过后财务 3 天内打款。",
        confidence=0.9,
        sources=["employee_handbook.txt"],
    )
    print(f"  {result.model_dump()}")

    print("""
💡 为什么 AI 开发离不开它？
    - 不用手写"参数类型检查"的代码，Pydantic 自动做
    - Field(description=...) 可以直接生成给 LLM 的 JSON Schema
    - 你项目的 03_function_calling/tools.py 里手写的
      JSON Schema，用 Pydantic 可以自动生成
""")
