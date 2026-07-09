"""
LLM Client：通用的 OpenAI 协议兼容客户端
支持任何兼容 OpenAI 接口的大模型（DeepSeek、OpenAI、Moonshot、本地模型等）

配置方式（.env 文件）：
    # 方式1：简单配置（单个模型）
    LLM_API_KEY=sk-xxx
    LLM_BASE_URL=https://api.deepseek.com/v1
    LLM_MODEL=deepseek-chat

    # 方式2：多模型配置（通过 provider 切换）
    LLM_DEFAULT_PROVIDER=deepseek

    DEEPSEEK_API_KEY=sk-xxx
    DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
    DEEPSEEK_MODEL=deepseek-chat

    OPENAI_API_KEY=sk-xxx
    OPENAI_BASE_URL=https://api.openai.com/v1
    OPENAI_MODEL=gpt-4o-mini
"""

import os
from openai import OpenAI
from dotenv import load_dotenv
from typing import List, Dict, Optional

# 加载 .env 配置文件
load_dotenv()


class LLMClient:
    """
    通用 LLM 客户端：任何兼容 OpenAI 协议的模型都能用

    用法：
        # 方式1：用默认 provider（.env 里配的 LLM_DEFAULT_PROVIDER）
        llm = LLMClient()

        # 方式2：指定 provider
        llm = LLMClient(provider="openai")

        # 方式3：直接传参（不走 .env）
        llm = LLMClient(
            api_key="sk-xxx",
            base_url="https://api.deepseek.com/v1",
            model="deepseek-chat",
        )

        # 对话
        reply = llm.chat("你好")
    """

    def __init__(
        self,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        temperature: float = 0.7,
    ):
        """
        初始化客户端

        优先级：直接传参 > provider 配置 > 通用配置

        Args:
            provider:    模型提供方，如 "deepseek"、"openai"，用于从 .env 读取对应配置
            model:       模型名称
            api_key:     API Key
            base_url:    API 地址
            temperature: 温度参数（0=确定，1=随机）
        """
        # 如果指定了 provider，按 provider 从环境变量读取
        if provider:
            prefix = provider.upper()
            api_key = api_key or os.getenv(f"{prefix}_API_KEY")
            base_url = base_url or os.getenv(f"{prefix}_BASE_URL")
            model = model or os.getenv(f"{prefix}_MODEL")

        # 如果没传，再尝试通用变量名（LLM_API_KEY / LLM_BASE_URL / LLM_MODEL）
        api_key = api_key or os.getenv("LLM_API_KEY")
        base_url = base_url or os.getenv("LLM_BASE_URL")
        model = model or os.getenv("LLM_MODEL")

        # 默认值兜底
        if not model:
            model = "deepseek-chat"  # 最后的兜底

        if not api_key:
            raise ValueError(
                "未找到 API Key！\n"
                "请在 .env 文件中配置以下任一组合：\n"
                "  通用：LLM_API_KEY + LLM_BASE_URL + LLM_MODEL\n"
                "  或指定 provider：DEEPSEEK_API_KEY + DEEPSEEK_BASE_URL + DEEPSEEK_MODEL\n"
                "  或初始化时直接传参：LLMClient(api_key=..., base_url=..., model=...)"
            )

        self.model = model
        self.temperature = temperature
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
            messages:     历史消息列表（可选）
            system_prompt: 系统提示词

        Returns:
            LLM 的回复文本
        """
        full_messages = [{"role": "system", "content": system_prompt}]
        if messages:
            full_messages.extend(messages)
        full_messages.append({"role": "user", "content": user_input})

        response = self.client.chat.completions.create(
            model=self.model,
            messages=full_messages,
            temperature=self.temperature,
        )
        return response.choices[0].message.content

    def chat_raw(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
    ) -> str:
        """
        直接发送原始 messages 列表（更灵活的调用方式）

        Args:
            messages:    完整的消息列表
            temperature: 可选的温度参数

        Returns:
            LLM 的回复文本
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature if temperature is not None else self.temperature,
        )
        return response.choices[0].message.content


# --- 测试 ---
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
