"""
LLM Client：封装 DeepSeek（兼容 OpenAI 协议）的调用
所有主题文件夹都可以复用这个模块
"""

import os
from openai import OpenAI
from dotenv import load_dotenv
from typing import List, Dict, Optional

# 加载根目录的 .env 配置文件
load_dotenv()


class LLMClient:
    """
    LLM 客户端：封装 DeepSeek（OpenAI 兼容协议）的调用

    用法：
        llm = LLMClient()
        reply = llm.chat("你好")
        # 或带历史消息
        reply = llm.chat("继续刚才的话题", messages=history)
    """

    def __init__(
        self,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        temperature: float = 0.7,
    ):
        """
        初始化客户端，参数不传则从 .env 读取

        Args:
            model:     模型名称，默认从 .env 读 DEEPSEEK_MODEL
            api_key:   API Key，默认从 .env 读 DEEPSEEK_API_KEY
            base_url:  API 地址，默认从 .env 读 DEEPSEEK_BASE_URL
            temperature: 温度参数，控制回复的随机性（0=确定，1=随机）
        """
        self.model = model or os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
        self.temperature = temperature

        api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        base_url = base_url or os.getenv("DEEPSEEK_BASE_URL")

        if not api_key:
            raise ValueError("未找到 API Key，请在 .env 文件中配置 DEEPSEEK_API_KEY")

        self.client = OpenAI(api_key=api_key, base_url=base_url)

    def chat(
        self,
        user_input: str,
        messages: Optional[List[Dict[str, str]]] = None,
        system_prompt: str = "你是一个有帮助的助手。",
    ) -> str:
        """
        发送消息给 LLM，返回回复文本

        Args:
            user_input:   用户输入的内容
            messages:     历史消息列表（可选），格式：[{"role": "user", "content": "..."}]
            system_prompt: 系统提示词，设定 Agent 的人设

        Returns:
            LLM 的回复文本
        """
        # 构建完整的消息列表
        full_messages = [{"role": "system", "content": system_prompt}]

        # 如果传了历史消息，追加进去
        if messages:
            full_messages.extend(messages)

        # 追加本次用户输入
        full_messages.append({"role": "user", "content": user_input})

        # 调用 API
        response = self.client.chat.completions.create(
            model=self.model,
            messages=full_messages,
            temperature=self.temperature,
        )

        # 提取回复文本
        return response.choices[0].message.content

    def chat_raw(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
    ) -> str:
        """
        直接发送原始 messages 列表（更灵活的调用方式）

        Args:
            messages: 完整的消息列表，格式：[{"role": "user", "content": "..."}]
            temperature: 可选的温度参数，不传则用默认值

        Returns:
            LLM 的回复文本
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature if temperature is not None else self.temperature,
        )
        return response.choices[0].message.content


# --- 直接运行此文件可以测试 ---
if __name__ == "__main__":
    try:
        llm = LLMClient()
        print("✅ LLM Client 初始化成功")
        print(f"   模型: {llm.model}")
        print(f"   温度: {llm.temperature}")
        print("\n--- 测试对话 ---")
        reply = llm.chat("你好，请用一句话介绍你自己")
        print(f"Agent: {reply}")
    except Exception as e:
        print(f"❌ 出错: {e}")
