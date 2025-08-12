# Model Management Integration

本次实现集成了模型选择、信息显示和设置功能到一个统一的 `ModelControl` 组件中。

## 新增组件

### 1. ModelControl
集成组件，包含：
- 模型选择下拉框
- Token 使用统计按钮
- 模型设置按钮

### 2. ModelContext
提供全局模型状态管理：
- 模型列表加载和缓存
- 当前选中模型跟踪
- 模型信息自动加载
- 提供模型操作方法

### 3. ModelInfoModal
显示详细模型信息：
- 基本信息（名称、类型、所有者、描述）
- Token 使用统计（总量、已用、剩余、使用率）
- 性能指标（响应时间、成功率）
- 使用记录（最后使用时间）

### 4. ModelSettingsModal
模型参数配置：
- Temperature（输出随机性控制）
- Max Tokens（最大输出长度）
- Top P（词汇多样性）
- 重置为默认值

## 使用方法

### 1. 在应用中集成 ModelProvider

```tsx
import { ModelProvider } from './context/ModelContext';

function App() {
  return (
    <UserSessionProvider>
      <ModelProvider>
        {/* 其他组件 */}
      </ModelProvider>
    </UserSessionProvider>
  );
}
```

### 2. 在组件中使用 ModelControl

```tsx
import { ModelControl } from './components/chat/ModelControl';

function ChatArea() {
  return (
    <div className="chat-input-toolbar">
      <div className="chat-input-tools-left">
        <ModelControl />
      </div>
    </div>
  );
}
```

### 3. 在其他组件中获取当前选中的模型

```tsx
import { useModel } from './hooks/useModel';

function SomeComponent() {
  const { selectedModel, selectedModelId, modelInfo } = useModel();
  
  return (
    <div>
      <p>当前模型: {selectedModel?.name}</p>
      <p>Token 使用量: {modelInfo?.tokenUsage?.used}</p>
    </div>
  );
}
```

## 接口设计

### ModelInfo 接口
模型信息接口设计为扩展性强，目前包含：
- `tokenUsage`: Token 使用统计
- `performance`: 性能指标
- `lastUsed`: 最后使用时间

未来可以扩展更多字段：
- 成本统计
- 使用频率
- 错误率统计
- 等等

### API 接口
当前使用模拟数据，未来需要实现的 API 端点：
- `GET /api/models/{modelId}/info` - 获取模型详细信息
- `GET /api/models/{modelId}/stats` - 获取模型统计数据
- `PUT /api/models/{modelId}/settings` - 保存模型设置

## 样式
添加了滑块组件的样式，支持深色模式和浅色模式。

## 状态管理
使用 React Context 进行状态管理，提供：
- 集中化的模型状态
- 自动缓存机制
- 异步数据加载
- 错误处理

## 扩展性
该设计具有良好的扩展性：
1. 可以轻松添加更多模型信息字段
2. 可以扩展模型设置参数
3. 可以添加更多模型操作功能
4. 支持多种模型类型
