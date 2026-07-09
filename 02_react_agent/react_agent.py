"""
ReAct Agent：推理（Reasoning）+ 行动（Acting）

核心循环：
    Thought（思考）→ Action（行动）→ Observation（观察）→ 循环
    直到 Action 是 Finish[最终答案]
"""

import re
from common.llm import LLMClient
from tools import ToolRegistry


# ============================================================
# ReAct 的 Prompt 模板
# 这是 ReAct 的灵魂：用 Prompt 约束 LLM 按格式输出
# ============================================================
REACT_PROMPT = """你是一个具备推理和行动能力的智能助手。
你可以通过思考分析问题，然后调用合适的工具来获取信息，最终给出准确的答案。

## 可用工具
{tools}

## 工作流程
请严格按照以下格式回应，每次只能执行一个步骤：

Thought: 你的思考过程，分析问题、规划下一步。
Action: 你的行动，必须是以下格式之一：
- `工具名[参数]` - 调用指定工具
- `Finish[最终答案]` - 当你有足够信息回答问题时使用

## 示例
Question: 3的平方加上4的平方是多少？
Thought: 我需要先算 3 的平方，再算 4 的平方，最后相加。
Action: Calculator[3**2]

Observation: 3**2 = 9

Thought: 现在我需要算 4 的平方。
Action: Calculator[4**2]

Observation: 4**2 = 16

Thought: 现在把两个结果相加：9 + 16 = 25。
Action: Finish[3的平方加上4的平方等于25]

## 当前任务
Question: {question}

## 执行历史
{history}

现在开始你的推理和行动：
"""


class ReActAgent:
    """
    ReAct Agent：推理与行动结合的智能体

    核心逻辑：
        1. 把问题 + 工具 + 历史 拼成 Prompt
        2. 调用 LLM 得到 Thought + Action
        3. 解析 Action：
           - Finish[答案] → 返回最终答案
           - 工具名[参数] → 执行工具 → 拿到 Observation → 加入历史 → 回到 1
    """

    def __init__(self, llm: LLMClient, tools: ToolRegistry, max_steps: int = 5):
        """
        Args:
            llm:       LLM 客户端
            tools:     工具注册器
            max_steps: 最大循环步数（防止死循环）
        """
        self.llm = llm
        self.tools = tools
        self.max_steps = max_steps

    def run(self, question: str) -> str:
        """运行 ReAct 循环，返回最终答案"""
        print(f"\n🤖 开始处理问题: {question}")
        history = []  # 执行历史，记录每一轮的 Action 和 Observation

        for step in range(1, self.max_steps + 1):
            print(f"\n{'='*50}")
            print(f"📍 第 {step} 步")
            print(f"{'='*50}")

            # ① 构建 Prompt
            prompt = REACT_PROMPT.format(
                tools=self.tools.description(),
                question=question,
                history="\n".join(history) if history else "（无）",
            )

            # ② 调用 LLM
            messages = [{"role": "user", "content": prompt}]
            response = self.llm.chat_raw(messages, temperature=0)  # temperature=0 让输出更稳定

            print(f"\n📝 LLM 原始输出:\n{response}")

            # ③ 解析输出
            thought, action = self._parse_output(response)

            if thought:
                print(f"\n🤔 Thought: {thought}")

            if not action:
                print("⚠️ 未能解析出 Action，流程终止")
                break

            # ④ 检查是否结束
            if action.startswith("Finish"):
                final_answer = self._extract_bracket(action)
                print(f"\n🎉 最终答案: {final_answer}")
                return final_answer

            # ⑤ 执行工具
            tool_name, tool_input = self._parse_action(action)
            print(f"\n🎬 Action: {tool_name}[{tool_input}]")

            if not tool_name:
                history.append(f"Action: {action}")
                history.append("Observation: 无效的 Action 格式")
                continue

            observation = self.tools.execute(tool_name, tool_input)
            print(f"\n👀 Observation: {observation}")

            # ⑥ 记录历史
            history.append(f"Action: {action}")
            history.append(f"Observation: {observation}")

        print(f"\n⚠️ 已达到最大步数 {self.max_steps}，流程终止")
        return "抱歉，我无法在限定步数内完成这个任务。"

    # ============================================================
    # 输出解析器：用正则从 LLM 输出中提取 Thought 和 Action
    # ============================================================

    def _parse_output(self, text: str):
        """
        从 LLM 输出中解析出 Thought 和 Action

        示例输入：
            Thought: 我需要先计算 3 的平方。
            Action: Calculator[3**2]

        返回：
            ("我需要先计算 3 的平方。", "Calculator[3**2]")
        """
        # 匹配 Thought: 到 Action: 之间的内容
        thought_match = re.search(r"Thought:\s*(.*?)(?=\nAction:|$)", text, re.DOTALL)
        # 匹配 Action: 到末尾的内容
        action_match = re.search(r"Action:\s*(.*?)$", text, re.DOTALL)

        thought = thought_match.group(1).strip() if thought_match else None
        action = action_match.group(1).strip() if action_match else None
        return thought, action

    def _parse_action(self, action: str):
        """
        从 Action 中解析出工具名和参数

        示例：Calculator[3**2] → ("Calculator", "3**2")
        """
        match = re.match(r"(\w+)\[(.*)\]", action, re.DOTALL)
        if match:
            return match.group(1), match.group(2)
        return None, None

    def _extract_bracket(self, text: str) -> str:
        """提取方括号中的内容：Finish[答案] → 答案"""
        match = re.search(r"\[(.*)\]", text, re.DOTALL)
        return match.group(1).strip() if match else text
