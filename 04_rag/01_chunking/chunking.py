"""
文本切片策略：滑动窗口 vs 语义切分

RAG 的第一个关键步骤：如何把长文档切成合适的片段？
切片质量直接影响检索效果。

两种主流策略：
    1. 滑动窗口（Sliding Window）：按固定长度切，带重叠
    2. 语义切分（Semantic Chunking）：按语义边界（句子/段落）切
"""

import re
from typing import List, Tuple


# ============================================================
# 策略一：滑动窗口（当前 vector_store.py 用的方法）
# ============================================================

def sliding_window_chunk(
    text: str,
    chunk_size: int = 200,
    overlap: int = 50,
) -> List[str]:
    """
    滑动窗口切片：固定长度 + 重叠

    原理：
        像一个固定大小的窗口在文本上滑动，每次移动 chunk_size - overlap
        相邻两段有 overlap 个字符的重叠，保证上下文不丢失

    优点：
        - 实现简单，可控性强
        - 保证每段长度均匀，不会超出 embedding 的 token 限制
        - 重叠机制减少信息截断

    缺点：
        - 可能在句子中间切断，破坏语义完整性
        - 不管内容是什么，都"一刀切"，不够智能

    适用场景：
        - 结构化文档（代码、日志、表格数据）
        - 需要严格控制片段长度的场景
    """
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size

        # 尽量在句号、换行等自然边界处切
        if end < len(text):
            for sep in ["\n\n", "\n", "。", "；", ".", ";"]:
                pos = text.rfind(sep, start, end)
                if pos > start:
                    end = pos + 1
                    break

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        start = end - overlap if end < len(text) else end

    return chunks


# ============================================================
# 策略二：语义切分（基于句子/段落边界）
# ============================================================

def semantic_chunk(
    text: str,
    max_chunk_size: int = 500,
    min_chunk_size: int = 50,
) -> List[str]:
    """
    语义切片：按照语义单元（段落 → 句子）组合

    原理：
        1. 先按段落分割（双换行）
        2. 再把大段落拆成句子
        3. 把短句子合并成不超过 max_chunk_size 的块
        保证每个块都是完整的语义单元

    优点：
        - 保留完整的句子和段落结构
        - 语义完整性好，检索时更容易匹配到有意义的内容
        - 不会在句子中间切断

    缺点：
        - 实现复杂度稍高
        - 某些段落可能仍然很长（需要二次拆分）
        - 短句合并时可能混合不同主题

    适用场景：
        - 自然语言文档（文章、书籍、说明书）
        - 对语义完整性要求高的场景
    """
    chunks = []

    # 第一步：按段落分割（双换行）
    paragraphs = re.split(r'\n\s*\n', text)

    current_chunk = ""

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        # 如果单个段落就超过 max_chunk_size，需要强制拆分
        if len(para) > max_chunk_size:
            # 先保存当前累积的 chunk
            if current_chunk.strip():
                chunks.append(current_chunk.strip())
                current_chunk = ""

            # 把超长段落按句子拆分
            sentences = _split_into_sentences(para)

            temp_chunk = ""
            for sent in sentences:
                sent = sent.strip()
                if not sent:
                    continue

                if len(temp_chunk) + len(sent) <= max_chunk_size:
                    temp_chunk += sent
                else:
                    if temp_chunk.strip():
                        chunks.append(temp_chunk.strip())
                    temp_chunk = sent

            if temp_chunk.strip():
                current_chunk = temp_chunk
                temp_chunk = ""

        else:
            # 正常段落：尝试合并到当前 chunk
            if len(current_chunk) + len(para) + 1 <= max_chunk_size:
                current_chunk += ("\n" + para) if current_chunk else para
            else:
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())
                current_chunk = para

    # 别忘了最后一个 chunk
    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    # 过滤掉太短的碎片
    return [c for c in chunks if len(c) >= min_chunk_size]


def _split_into_sentences(text: str) -> List[str]:
    """
    把文本拆分成句子列表

    中文句子结束符：。！？……
    英文句子结束符：.!?
    """
    # 用正则匹配句子边界
    pattern = r'(?<=[。！？…\.!\?])\s*'
    sentences = re.split(pattern, text)
    return [s.strip() for s in sentences if s.strip()]


# ============================================================
# 策略三：递归字符切分（LangChain 默认策略）
# ============================================================

def recursive_character_chunk(
    text: str,
    chunk_size: int = 200,
    overlap: int = 50,
    separators: List[str] = None,
) -> List[str]:
    """
    递归字符切分：用一系列分隔符逐级尝试

    原理（这是 LangChain RecursiveCharacterTextSplitter 的核心思想）：
        按优先级尝试不同的分隔符：
        1. "\n\n" （段落分隔）
        2. "\n"   （行分隔）
        3. "。"   （中文句号）
        4. "；"   （中文分号）
        5. "，"   （中文逗号）
        6. " "    （空格）
        7. ""     （字符级别，最后手段）

        如果用某个分隔符切出来的段还是太长，就用下一个级别的分隔符继续切

    优点：
        - 层级化切分，尽量保持语义完整
        - 是目前工业界最常用的方案（LangChain 默认）
        - 兼顾了语义和长度控制

    缺点：
        - 对中文的分隔符顺序需要调优
        - 递归实现有一定开销

    这是生产环境最推荐的方案 👈
    """
    if separators is None:
        # 中文友好的分隔符优先级
        separators = ["\n\n", "\n", "。", "；", "，", " ", ""]

    return _recursive_split(text, chunk_size, overlap, separators)


def _recursive_split(
    text: str,
    chunk_size: int,
    overlap: int,
    separators: List[str],
) -> List[str]:
    """递归切分的核心实现"""

    # 基础情况：没有更多分隔符了，直接按长度切
    if not separators or separators == [""]:
        return sliding_window_chunk(text, chunk_size, overlap)

    # 取当前优先级的分隔符
    separator = separators[0]
    remaining_separators = separators[1:]

    # 用当前分隔符分割
    parts = text.split(separator)

    chunks = []
    current_chunk = ""

    for part in parts:
        part = part.strip() if separator else part

        if not part:
            continue

        # 如果加上这段后还没超限，继续累积
        proposed = current_chunk + (separator + part if current_chunk else part)

        if len(proposed) <= chunk_size:
            current_chunk = proposed
        else:
            # 当前 chunk 已经满了，保存它
            if current_chunk:
                chunks.append(current_chunk)

            # 如果单段就超长了，用下一级分隔符递归切分
            if len(part) > chunk_size:
                sub_chunks = _recursive_split(part, chunk_size, overlap, remaining_separators)
                chunks.extend(sub_chunks)
                current_chunk = ""
            else:
                current_chunk = part

    # 保存最后一个 chunk
    if current_chunk:
        chunks.append(current_chunk)

    return chunks


# ============================================================
# 对比实验
# ============================================================

def compare_strategies(text: str) -> dict:
    """
    对比三种切片策略的效果

    返回统计信息，方便直观比较
    """
    print("=" * 60)
    print("📊 文本切片策略对比")
    print("=" * 60)
    print(f"原始文本长度: {len(text)} 字符\n")

    results = {}

    # ---- 策略一：滑动窗口 ----
    chunks_sw = sliding_window_chunk(text, chunk_size=200, overlap=50)
    results["sliding_window"] = chunks_sw
    print(f"【策略一】滑动窗口 (chunk_size=200, overlap=50)")
    print(f"   切片数量: {len(chunks_sw)}")
    print(f"   平均长度: {sum(len(c) for c in chunks_sw) / len(chunks_sw):.0f} 字符")
    print(f"   最短/最长: {min(len(c) for c in chunks_sw)} / {max(len(c) for c in chunks_sw)} 字符")
    print(f"   示例[0]: {chunks_sw[0][:80]}...")
    print()

    # ---- 策略二：语义切分 ----
    chunks_sem = semantic_chunk(text, max_chunk_size=500, min_chunk_size=50)
    results["semantic"] = chunks_sem
    print(f"【策略二】语义切分 (max_chunk=500, min_chunk=50)")
    print(f"   切片数量: {len(chunks_sem)}")
    if chunks_sem:
        print(f"   平均长度: {sum(len(c) for c in chunks_sem) / len(chunks_sem):.0f} 字符")
        print(f"   最短/最长: {min(len(c) for c in chunks_sem)} / {max(len(c) for c in chunks_sem)} 字符")
        print(f"   示例[0]: {chunks_sem[0][:80]}...")
    print()

    # ---- 策略三：递归字符切分 ----
    chunks_rec = recursive_character_chunk(text, chunk_size=200, overlap=50)
    results["recursive"] = chunks_rec
    print(f"【策略三】递归字符切分 (chunk_size=200, overlap=50)")
    print(f"   切片数量: {len(chunks_rec)}")
    print(f"   平均长度: {sum(len(c) for c in chunks_rec) / len(chunks_rec):.0f} 字符")
    print(f"   最短/最长: {min(len(c) for c in chunks_rec)} / {max(len(c) for c in chunks_rec)} 字符")
    print(f"   示例[0]: {chunks_rec[0][:80]}...")
    print()

    return results


if __name__ == "__main__":
    # 用我们的知识库测试
    with open("knowledge_base.txt", "r", encoding="utf-8") as f:
        text = f.read()

    results = compare_strategies(text)

    # 额外展示：检查每个策略的切片是否在句子中间断开
    print("=" * 60)
    print("🔍 质量检查：是否有切片在句子中间断开？")
    print("=" * 60)

    for name, chunks in results.items():
        broken_count = 0
        for chunk in chunks:
            # 如果切片不以标点或空白结尾，可能是在句子中间切断的
            if chunk and chunk[-1] not in "。\n.!?\n\r":
                broken_count += 1
        ratio = broken_count / len(chunks) * 100 if chunks else 0
        status = "⚠️  较多" if ratio > 30 else ("✅ 较少" if ratio > 0 else "✅ 完美")
        print(f"{name}: {broken_count}/{len(chunks)} 段可能被截断 ({ratio:.0f}%) {status}")
