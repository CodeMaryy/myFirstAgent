# AI 高频 Python 特性清单

> 给"学完就忘"的解药：**每个特性只在项目里用一次，用过的才算学会。**

## 🧭 学习原则

1. **学用一体** —— 每个特性配一个最小可运行 demo，跑通即完成
2. **20 分钟原则** —— 单个特性只练 20 分钟，不贪多
3. **重写 > 重看** —— 忘记时凭记忆重写，而不是重看笔记
4. **联系场景** —— 每个特性记住一个 AI 应用场景，面试能讲出"我用它做过什么"

## ⭐⭐⭐ 必学（AI 开发天天用）

| # | 特性 | AI 应用场景 | 练习文件 | 状态 |
|---|------|-------------|---------|------|
| 1 | `async` / `await` 协程 | 并发调用多个 LLM / 多数据源搜索 | [01_async_demo.py](python_practice/01_async_demo.py) | ⬜ |
| 2 | `yield` 生成器 | LLM 流式输出（打字机效果） | [02_yield_stream.py](python_practice/02_yield_stream.py) | ⬜ |
| 3 | 装饰器 `@decorator` | LLM 调用耗时统计 / 失败重试 / 工具注册 | [03_decorator.py](python_practice/03_decorator.py) | ⬜ |
| 4 | `with` 上下文管理器 | API 连接、文件读写 | 已在项目中使用 | ✅ |
| 5 | 类型注解 `List[str] / Dict` | 函数签名、代码可读性 | 已在 `04_rag` 中使用 | ✅ |

## ⭐⭐ 进阶（做项目会用到）

| # | 特性 | AI 应用场景 | 练习文件 | 状态 |
|---|------|-------------|---------|------|
| 6 | `Pydantic` 数据模型 | 定义工具参数、结构化输出 | [04_pydantic_demo.py](python_practice/04_pydantic_demo.py) | ⬜ |
| 7 | 生成器表达式 `(x for x in d)` | 大向量库惰性处理，省内存 | [05_generator_expr.py](python_practice/05_generator_expr.py) | ⬜ |
| 8 | `enumerate` / `zip` / `dict.get` | 数据处理瑞士军刀 | 项目里零散使用 | ✅ |

## ⬜ 可以跳过（投入产出比低，面试几乎不问）

- 元类（metaclass）、描述符（descriptor）、多重继承 MRO、`__slots__`

## 📌 项目实战对照表

每个特性在 `myFirstAgent` 项目里的落点：

| 特性 | 项目里的位置 |
|------|--------------|
| 类型注解 | `04_rag/vector_store.py` 的函数签名 |
| `with` | `with open(...)` 读文件、`load_dotenv()` |
| `async/await` | 计划加入：`05_linear_chat` 的多模型并发调用 |
| `yield` | 计划加入：`06_streaming` 的流式输出 |
| 装饰器 | 计划加入：`07_tool_registry` 的工具自动注册 |

## 🔄 复习节奏建议

```
Day 1  跑通所有 demo（照着代码抄一遍）
Day 3  凭记忆重写 01、02
Day 7  凭记忆重写 03、04
Day 14 凭记忆重写 05，并在项目里用一次
```
