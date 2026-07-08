"""
工具模块：工具注册器 + 具体工具实现
ReAct Agent 通过工具来"行动"，获取外部信息
"""

from typing import Dict, Any, Callable, Optional


class ToolRegistry:
    """
    工具注册器：管理所有可用工具
    Agent 通过它来注册、查询、执行工具
    """

    def __init__(self):
        self.tools: Dict[str, Dict[str, Any]] = {}

    def register(self, name: str, description: str, func: Callable):
        """注册一个工具"""
        self.tools[name] = {"description": description, "func": func}
        print(f"🛠️  工具已注册: {name}")

    def get(self, name: str) -> Optional[Callable]:
        """根据名称获取工具函数"""
        tool = self.tools.get(name)
        return tool["func"] if tool else None

    def execute(self, name: str, input_str: str) -> str:
        """执行工具并返回结果（字符串）"""
        func = self.get(name)
        if not func:
            return f"错误：未找到工具 '{name}'"
        try:
            return str(func(input_str))
        except Exception as e:
            return f"工具执行出错: {e}"

    def description(self) -> str:
        """获取所有工具的描述（拼成字符串，塞进 Prompt 用）"""
        return "\n".join(
            f"- {name}: {info['description']}"
            for name, info in self.tools.items()
        )


# ============================================================
# 具体工具实现
# ============================================================

def calculator(expression: str) -> str:
    """
    计算器工具：执行数学运算
    输入：数学表达式字符串，如 "2 + 3 * 4"
    输出：计算结果
    """
    # 安全检查：只允许数字和基本运算符
    allowed = set("0123456789+-*/(). ")
    if not all(c in allowed for c in expression):
        return "错误：表达式包含非法字符"

    result = eval(expression)  # 注意：生产环境不要用 eval，这里仅为演示
    return f"{expression} = {result}"


def fake_search(query: str) -> str:
    """
    模拟搜索工具（不调真实 API，返回预设结果）
    输入：搜索关键词
    输出：搜索结果
    """
    # 预设一些"搜索结果"，让 Agent 能用
    mock_data = {
        "北京天气": "北京今天 25 度，晴",
        "上海天气": "上海今天 28 度，多云",
        "美团": "美团是中国领先的生活服务电子商务平台",
        "deepseek": "DeepSeek 是一家中国 AI 公司，专注大模型研发",
    }

    # 模糊匹配
    for key, value in mock_data.items():
        if key in query:
            return value

    return f"搜索 '{query}' 未找到相关结果"


# ============================================================
# 测试
# ============================================================
if __name__ == "__main__":
    registry = ToolRegistry()
    registry.register("Calculator", "数学计算器，输入数学表达式返回结果", calculator)
    registry.register("Search", "搜索引擎，搜索实时信息", fake_search)

    print("\n--- 工具描述 ---")
    print(registry.description())

    print("\n--- 测试计算器 ---")
    print(registry.execute("Calculator", "2 + 3 * 4"))

    print("\n--- 测试搜索 ---")
    print(registry.execute("Search", "北京天气"))
