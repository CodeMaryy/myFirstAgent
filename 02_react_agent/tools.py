"""
工具模块：工具注册器 + 具体工具实现
ReAct Agent 通过工具来"行动"，获取外部信息
"""

import requests
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


# 城市名 → 经纬度的映射（Open-Meteo 需要经纬度来查天气）
CITY_COORDS = {
    "北京": (39.9042, 116.4074),
    "上海": (31.2304, 121.4737),
    "广州": (23.1291, 113.2644),
    "深圳": (22.5431, 114.0579),
    "成都": (30.5728, 104.0668),
    "杭州": (30.2741, 120.1551),
    "武汉": (30.5928, 114.3055),
    "西安": (34.3416, 108.9398),
    "南京": (32.0603, 118.7969),
    "重庆": (29.5630, 106.5516),
    "天津": (39.3434, 117.3616),
    "苏州": (31.2989, 120.5853),
}


def get_weather(city: str) -> str:
    """
    天气查询工具：调用 Open-Meteo 免费 API 获取真实天气
    输入：城市名（如 "北京"、"上海"）
    输出：当前温度、风速、天气状况
    """
    city = city.strip()

    # 查找城市经纬度
    coords = CITY_COORDS.get(city)
    if not coords:
        return f"未找到城市 '{city}'，目前支持查询的城市：{'、'.join(CITY_COORDS.keys())}"

    lat, lon = coords

    # 调用 Open-Meteo API（免费、无需 API Key）
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

    # 解析天气数据
    current = data.get("current", {})
    temp = current.get("temperature_2m", "未知")
    wind = current.get("wind_speed_10m", "未知")
    code = current.get("weather_code", 0)

    # weather_code 转中文描述（WMO 标准简化版）
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
# 测试
# ============================================================
if __name__ == "__main__":
    registry = ToolRegistry()
    registry.register("Calculator", "数学计算器，输入数学表达式返回结果", calculator)
    registry.register("Weather", "天气查询工具，输入城市名返回当前天气信息", get_weather)

    print("\n--- 工具描述 ---")
    print(registry.description())

    print("\n--- 测试计算器 ---")
    print(registry.execute("Calculator", "2 + 3 * 4"))

    print("\n--- 测试天气 ---")
    print(registry.execute("Weather", "北京"))
