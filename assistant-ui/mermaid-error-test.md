# Mermaid 错误处理测试

这个文件用于测试 Mermaid 图表的错误处理能力。

## 正常的流程图
```mermaid
flowchart TD
    A[开始] --> B{条件判断}
    B -->|是| C[执行操作A]
    B -->|否| D[执行操作B]
    C --> E[结束]
    D --> E
```

## 包含 Font Awesome 图标的流程图（应该会被自动修复）
```mermaid
flowchart TD
    A[Christmas] -->|Get money| B(Go shopping)
    B --> C{Let me think}
    C -->|One| D[Laptop]
    C -->|Two| E[iPhone]
    C -->|Three| F[fa:fa-car Car]
    F --> G[fa:fa-home Home]
```

## 包含语法错误的图表（应该显示错误信息）
```mermaid
flowchart TD
    A[开始] --> B{
    B -->|是| C[操作A
    C --> D[结束
```

## 正常的时序图
```mermaid
sequenceDiagram
    participant A as 用户
    participant B as 系统
    A->>B: 请求
    B-->>A: 响应
```

如果以上图表能正确显示或显示友好的错误信息，说明错误处理工作正常。
