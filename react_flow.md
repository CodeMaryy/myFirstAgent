```mermaid
flowchart TD
    A[用户输入问题] --> B[构建 Prompt<br/>工具描述 + 问题 + 历史记录]
    B --> C[调用 LLM think]
    C --> D{解析输出}
    
    D -->|Thought + Action| E{Action 类型?}
    D -->|解析失败| F[⚠️ 流程终止]
    
    E -->|Finish[答案]| G[🎉 返回最终答案]
    E -->|工具调用[参数]| H[执行工具]
    H --> I[获取 Observation]
    I --> J[记录到历史记录]
    J --> B
    
    style A fill:#e1f5fe
    style C fill:#fff3e0
    style G fill:#c8e6c9
    style F fill:#ffcdd2
    style H fill:#f3e5f5
```
```mermaid
flowchart TD
    User["用户输入问题"] --> Agent["Agent 主循环"]

    Agent --> Prompt["构造 Prompt"]
    Agent --> History["读取历史消息"]
    Agent --> Tools["读取可用工具列表"]

    Prompt --> LLM["HelloAgentsLLM"]
    History --> LLM
    Tools --> LLM

    LLM --> Output["模型输出"]

    Output --> Judge{"是否要调用工具？"}

    Judge -->|否| Answer["生成最终回答"]
    Answer --> Save["保存到 Message History"]
    Save --> UserOut["返回给用户"]

    Judge -->|是| ToolCall["解析工具调用"]
    ToolCall --> Registry["ToolRegistry 工具注册表"]
    Registry --> Tool["执行具体工具"]

    Tool --> Observation["工具执行结果 Observation"]
    Observation --> Agent
```