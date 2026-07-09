"""
工具模块：工具函数 + JSON Schema 声明

和 02_react_agent/tools.py 的区别：
    - 02：工具描述写在 Prompt 文本里（给 LLM 看的自然语言）
    - 03：工具描述用 JSON Schema 声明（给 LLM 看的结构化格式）

JSON Schema 告诉 LLM：
    "有哪些工具可以用、每个工具需要什么参数、参数是什么类型"
    LLM 就能返回结构化的工具调用，不需要正则解析
"""

import requests
from typing import Dict, Any, Callable, List


# ============================================================
# 工具函数（和 02 的一样，纯业务逻辑）
# ============================================================

def calculator(expression: str) -> str:
    """计算器：执行数学运算"""
    allowed = set("0123456789+-*/(). ")
    if not all(c in allowed for c in expression):
        return "错误：表达式包含非法字符"
    result = eval(expression)
    return f"{expression} = {result}"


# 城市经纬度
CITY_COORDS = {
    "北京": (39.9042, 116.4074),
    "上海": (31.2304, 121.4737),
    "广州": (23.1291, 113.2644),
    "深圳": (22.5431, 114.0579),
    "成都": (30.5728, 104.0668),
    "杭州": (30.2741, 120.1551),
}


def get_weather(city: str) -> str:
    """天气查询：调用 Open-Meteo API"""
    coords = CITY_COORDS.get(city.strip())
    if not coords:
        return f"未找到城市 '{city}'，支持：{'、'.join(CITY_COORDS.keys())}"

    lat, lon = coords
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,wind_speed_10m,weather_code",
        "timezone": "Asia/Shanghai",
    }

    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        return f"查询天气失败: {e}"

    current = data.get("current", {})
    temp = current.get("temperature_2m", "未知")
    wind = current.get("wind_speed_10m", "未知")
    code = current.get("weather_code", 0)

    weather_desc = {
        0: "晴", 1: "晴", 2: "多云", 3: "阴",
        45: "雾", 48: "雾",
        51: "小雨", 53: "小雨", 55: "中雨",
        61: "小雨", 63: "中雨", 65: "大雨",
        71: "小雪", 73: "中雪", 75: "大雪",
        80: "阵雨", 81: "阵雨", 82: "暴雨",
        95: "雷暴", 96: "雷暴", 99: "雷暴",
    }.get(code, f"未知(代码{code})")

    return f"{city}：当前温度 {temp}°C，{weather_desc}，风速 {wind} km/h"


# ============================================================
# 工具注册器：用 JSON Schema 声明工具
# 这是和 ReAct 版本最大的区别！
# ============================================================

class ToolManager:
    """
    工具管理器：管理工具函数 + 生成 OpenAI 格式的工具声明

    核心区别：
        ReAct 版：工具描述是纯文本，塞进 Prompt
        本版本：  工具描述是 JSON Schema，通过 tools 参数传给 LLM
    """

    def __init__(self):
        # 存储工具函数：{name: func}
        self.functions: Dict[str, Callable] = {}
        # 存储工具声明（JSON Schema 格式）
        self.schemas: List[Dict[str, Any]] = []

    def register(
        self,
        name: str,
        description: str,
        func: Callable,
        parameters: Dict[str, Any],
    ):
        """
        注册工具

        Args:
            name:        工具名称（LLM 会用这个名字调用）
            description: 工具描述（告诉 LLM 这个工具是干嘛的）
            func:        实际执行的函数
            parameters:  参数的 JSON Schema（告诉 LLM 需要什么参数）
        """
        self.functions[name] = func
        self.schemas.append({
            "type": "function",
            "function": {
                "name": name,
                "description": description,
                "parameters": parameters,
            },
        })
        print(f"🛠️  工具已注册: {name}")

    def get_schemas(self) -> List[Dict[str, Any]]:
        """获取所有工具的 JSON Schema（传给 LLM 的 tools 参数）"""
        return self.schemas

    def execute(self, name: str, arguments: Dict[str, Any]) -> str:
        """执行工具：根据函数名和参数调用对应函数"""
        func = self.functions.get(name)
        if not func:
            return f"错误：未找到工具 '{name}'"
        try:
            return str(func(**arguments))
        except Exception as e:
            return f"工具执行出错: {e}"


# ============================================================
# 创建默认的工具管理器（注册计算器和天气工具）
# ============================================================

def create_default_tools() -> ToolManager:
    """创建并返回一个注册了计算器和天气工具的 ToolManager"""
    manager = ToolManager()

    # 注册计算器
    manager.register(
        name="calculator",
        description="数学计算器，输入数学表达式返回计算结果",
        func=calculator,
        parameters={
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "数学表达式，如 2+3*4、35.8-30.6",
                },
            },
            "required": ["expression"],
        },
    )

    # 注册天气工具
    manager.register(
        name="get_weather",
        description="天气查询工具，输入城市名返回当前天气信息",
        func=get_weather,
        parameters={
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "城市名，如 北京、上海、广州",
                },
            },
            "required": ["city"],
        },
    )

    return manager


if __name__ == "__main__":
    manager = create_default_tools()

    print("\n--- 工具 Schema（传给 LLM 的格式）---")
    import json
    print(json.dumps(manager.get_schemas(), ensure_ascii=False, indent=2))

    print("\n--- 测试计算器 ---")
    print(manager.execute("calculator", {"expression": "2 + 3 * 4"}))

    print("\n--- 测试天气 ---")
    print(manager.execute("get_weather", {"city": "北京"}))
