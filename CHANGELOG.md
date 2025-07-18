# 变更日志

## [未发布] - 2025-07-18

### 重构优化 🎯

#### 主要改进

- **代码架构重构**: 将1400+行的巨型组件拆分成模块化架构
  - App.tsx从1418行减少到421行 (减少70%)
  - 创建了4个自定义hooks和6个可复用组件
  - 提升代码可读性和可维护性

- **模块化设计**: 实现清晰的关注点分离
  - `hooks/`: useAuth, useConversations, useFileUpload, useTheme
  - `components/`: Sidebar, MessageComponent, LoadingIndicator, ChatInput, MarkdownRenderer, AssistantAvatar
  - `utils/`: conversationUtils, styles (样式工具函数)

- **代码重复消除**:
  - 移除了3处重复的`getFileIcon`函数定义
  - 统一使用`useFileUpload` hook中的实现
  - 优化了`generateAIResponse`函数的参数传递

#### 技术改进

- **样式系统优化**: 引入了`themeClasses`工具函数用于一致的主题样式
- **TypeScript优化**: 改进了类型声明文件，简化了vite-env.d.ts
- **构建优化**: 移除了冗余文件，修复了所有编译错误

#### 文件清理

- 删除了有93个编译错误的重复App.tsx文件
- 移除了不必要的react-jsx.d.ts类型声明
- 清理了WSL环境下的npm配置问题

### 已解决的问题

- 修复了所有TypeScript编译错误
- 解决了npm路径配置在WSL环境下的问题
- 修复了代码重复导致的维护性问题

## [未发布] - 2025-07-17

### 新增功能

- **自动滚动到最新消息**: 修复了聊天界面的用户体验问题
  - 当发送新消息时，界面会自动滚动到最新消息
  - 当接收到AI回复时，界面会自动滚动到最新消息  
  - 当切换对话时，界面会自动滚动到该对话的最新消息
  - 消息加载过程中也会保持正确的滚动位置

### 技术实现

- 为消息显示容器添加了 `messagesContainerRef` 引用
- 通过两个 `useEffect` 钩子监听消息变化和对话切换
- 使用 `scrollTop = scrollHeight` 实现平滑滚动到底部

### 修复的问题

- 解决了新消息到来后需要手动滚动才能看到的不便问题
- 提升了聊天体验的流畅性和直观性
