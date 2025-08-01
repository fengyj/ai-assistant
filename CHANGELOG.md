# 变更日志

## [未发布] - 2025-08-01

### 新功能 ✨

- **聊天功能核心实现**: 完成基础聊天交互功能
  - 实现ConversationContext状态管理系统
  - 添加useChatInput自定义Hook处理输入逻辑
  - 支持消息发送和接收（模拟AI回复）
  - 集成输入框自动调整高度功能
  - 添加Ctrl+Enter快捷键发送消息
  - 实现发送按钮状态管理和加载动画
  - 支持中文输入法和输入验证

- **项目架构完善**: 建立完整的目录结构和基础设施
  - 创建api、utils、styles等核心目录
  - 实现ConversationProvider状态提供者
  - 添加useConversation Hook便于组件消费状态
  - 集成对话管理功能（创建、切换、删除对话）

### Bug 修复 🐛

- **模块导入错误修复**: 解决ConversationContextType导入问题
  - 修复TypeScript类型导出冲突
  - 优化模块导入路径和方式

- **主题切换功能修复**: 解决了暗色/亮色主题切换不生效的问题
  - 配置Tailwind CSS v4的dark mode使用class策略: `@variant dark (&:where(.dark, .dark *))`
  - 优化ThemeContext实现，正确处理localStorage和系统偏好
  - 添加防FOUC（Flash of Unstyled Content）脚本到HTML头部
  - 确保主题状态正确应用到DOM元素

### 代码清理 🧹

- 移除临时调试文件和测试组件
  - 删除 `debug.html`
  - 删除 `SimpleThemeTest.tsx`
  - 删除 `debug/` 组件目录

## [未发布] - 2025-07-19

### 样式架构重构 🎨

#### 主要更新

- **CSS架构重构**: 使用@apply指令创建语义化组件样式
  - 将内联Tailwind类重构为语义化CSS类名
  - 创建了100+个组件级样式类，提升代码可维护性
  - 实现更好的样式组织和复用

- **语义化样式系统**: 建立清晰的样式命名规范
  - 布局组件: `.app-container`, `.main-layout`, `.sidebar-container`, `.main-content`
  - 消息组件: `.message-bubble-user`, `.message-bubble-ai`, `.message-actions`
  - 按钮组件: `.btn-primary`, `.btn-secondary`, `.btn-icon`, `.btn-action`
  - 侧边栏组件: `.sidebar`, `.sidebar-header`, `.conversation-item`
  - 输入组件: `.chat-input-container`, `.chat-input-area`, `.chat-input-field`

- **组件更新**: 更新所有React组件使用新的语义化CSS类
  - App.tsx: 使用`.app-container`替代内联类
  - MainLayout.tsx: 使用`.main-layout`和`.sidebar-container`
  - Sidebar.tsx: 使用完整的侧边栏样式系统
  - ChatArea.tsx: 使用聊天区域专用样式类
  - Button.tsx: 简化为语义化按钮类

- **样式优化**: 改进的样式架构带来更好的开发体验
  - 更清晰的样式组织结构
  - 更好的样式复用和维护性
  - 统一的设计系统实现

## [2025-07-18] - 代码架构重构

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

## [2025-07-20] - Migrate PostCSS config to Vite

- Removed postcss.config.js from assistant-ui
- Integrated TailwindCSS PostCSS plugin directly in vite.config.ts
- Now all PostCSS plugins are managed via Vite config
