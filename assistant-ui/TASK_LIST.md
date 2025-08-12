

基于 README.md 需求分析的详细实施计划

## 🎯 界面设计分析

根据README.md，界面采用经典的左右分栏布局：

- **左侧侧边栏**：历史对话列表 + 用户状态栏
- **右侧主界面**：对话标题栏 + 消息列表 + 输入区域（三层结构）

## 🎨 样式设计方案

- 使用 Tailwind CSS 的 dark/light 模式
- 采用 CSS Variables 定义主题色
- 组件化设计，便于复用和维护
- 极致紧凑的设计理念

## 📋 详细任务列表

### Phase 1: 项目初始化与基础设置

#### 1.1 清理并重新初始化项目

- [x] 备份现有代码
- [x] 清理 assistant-ui 目录
- [x] 重新初始化 Vite + React + TypeScript 项目

#### 1.2 安装核心依赖

- [x] React 19 + TypeScript
- [x] Vite (最新版本)
- [x] Tailwind CSS (最新版本)
- [x] PostCSS + Autoprefixer

#### 1.3 安装UI相关依赖

- [x] @heroicons/react (图标库)
- [x] react-intl (国际化)
- [x] clsx (条件样式工具)

#### 1.4 安装功能依赖

- [x] axios (API 请求)
- [x] react-markdown (Markdown 渲染)
- [x] prism-react-renderer (代码高亮)
- [x] mermaid (图表渲染)
- [x] react-dropzone (文件上传)

#### 1.5 配置Tailwind CSS主题系统

- [x] 配置 dark/light 模式
- [x] 定义自定义颜色变量
- [x] 设置紧凑间距系统
- [x] 配置自定义动画

#### 1.6 设置基础目录结构

- [x] 创建 src/components/ 目录
- [x] 创建 src/pages/ 目录
- [x] 创建 src/api/ 目录
- [x] 创建 src/context/ 目录
- [x] 创建 src/styles/ 目录
- [x] 创建 src/types/ 目录
- [x] 创建 src/utils/ 目录
- [x] 创建 src/hooks/ 目录

### Phase 2: 核心架构搭建

#### 2.1 创建Context状态管理系统

- [x] ThemeContext (主题切换)
- [ ] UserContext (用户状态)
- [x] ConversationContext (对话管理)
- [x] UIContext (界面状态，如侧边栏折叠)

#### 2.2 创建基础类型定义

- [x] User 类型
- [x] Message 类型
- [x] Conversation 类型
- [x] Theme 类型
- [x] API 响应类型

#### 2.3 创建API层基础结构

- [ ] axios 配置
- [ ] API 基础类
- [ ] 错误处理机制
- [ ] 请求拦截器

#### 2.4 创建样式工具函数

- [ ] 主题工具函数
- [ ] 样式组合函数
- [ ] 响应式工具

### Phase 3: 基础组件开发

#### 3.1 布局组件

- [x] MainLayout (主布局组件)
- [x] Sidebar (侧边栏布局)
- [x] ChatArea (聊天区域布局)

#### 3.2 UI基础组件

- [x] Button (多种变体：primary, secondary, icon)
- [ ] Input (支持单行/多行，自动调整高度)
- [ ] Avatar (用户头像)
- [ ] LoadingIndicator (加载动画)
- [ ] Dropdown (下拉菜单)
- [ ] Modal (模态框)
- [ ] Tooltip (提示框)

#### 3.3 主题切换组件

- [x] ThemeToggle (主题切换按钮)
- [x] ThemeProvider (主题提供者)

#### 3.4 用户状态组件

- [ ] UserStatus (用户状态栏)
- [ ] LoginModal (登录弹窗)
- [ ] SettingsModal (设置弹窗)

### Phase 4: 核心功能组件

#### 4.1 侧边栏组件

- [ ] ConversationList (对话列表)
- [ ] ConversationGroup (按时间分组)
- [ ] ConversationItem (单个对话项)
- [ ] SidebarToggle (侧边栏折叠按钮)

#### 4.2 消息组件

- [ ] MessageBubble (消息气泡)
- [ ] MessageActions (消息操作按钮) - 已实现完整的消息操作功能
- [ ] MessageTimestamp (时间戳)
- [ ] UserMessage (用户消息)
- [ ] AIMessage (AI消息)

#### 4.3 Markdown渲染组件

- [ ] MarkdownRenderer (主渲染器)
- [ ] CodeBlock (代码块 + 语法高亮)
- [ ] MermaidDiagram (Mermaid图表)
- [ ] CopyButton (复制按钮)
- [ ] ImageZoom (图片放大)

#### 4.4 输入区域组件

- [x] ChatInput (三层输入区域) - 基础功能已实现
- [x] FileUpload (文件上传区域) - 完成拖拽上传、文件预览、粘贴支持
- [x] Toolbar (工具栏) - 基础界面和ModelSelector完成
- [x] ModelSelector (模型选择) - 完成高级模型选择器组件
- [ ] TokenStats (token统计)
- [ ] NotificationIcon (通知图标)

### Phase 5: 页面整合与优化

#### 5.1 主页面组件整合

- [x] ChatPage (聊天主页面)
- [x] 组件间数据流
- [x] 事件处理机制

#### 5.2 响应式布局优化

- [ ] 移动端适配
- [ ] 平板端适配
- [ ] 大屏幕优化

#### 5.3 交互动画添加

- [ ] 页面切换动画
- [ ] 消息发送动画
- [ ] 悬停效果
- [x] 加载状态动画 - 已实现基础加载动画

#### 5.4 无障碍功能完善

- [ ] ARIA 标签
- [ ] 键盘导航
- [ ] 屏幕阅读器支持
- [ ] 焦点管理

### Phase 6: 功能特性实现

#### 6.1 文件处理

- [x] 拖拽上传 - 完成拖拽上传功能
- [x] 粘贴上传 - 完成粘贴文件支持
- [x] 文件预览 - 完成文件信息预览
- [x] 文件删除 - 完成文件移除功能

#### 6.2 键盘快捷键

- [x] Ctrl+Enter 发送
- [ ] 其他快捷键支持

#### 6.3 消息操作

- [x] 复制消息 - 支持复制到剪贴板，兼容不同浏览器
- [x] 编辑消息 - 用户消息编辑功能，带编辑模态框
- [x] 重新生成 - AI消息重新生成功能
- [x] 点赞/点踩 - 消息反馈功能，状态持久化

#### 6.4 对话管理

- [ ] 新建对话
- [ ] 删除对话
- [ ] 对话标题编辑
- [ ] 历史对话加载

### Phase 7: 测试与优化

#### 7.1 组件测试

- [ ] 基础组件单元测试
- [ ] 复合组件集成测试
- [ ] 用户交互测试

#### 7.2 性能优化

- [ ] 代码分割
- [ ] 懒加载
- [ ] 内存优化
- [ ] 渲染优化

#### 7.3 国际化

- [ ] 中文文案
- [ ] 英文文案
- [ ] 语言切换机制

## 📝 实施注意事项

### 设计原则

1. **极致紧凑**：减少不必要的padding和margin
2. **现代美观**：使用圆角、阴影、渐变等现代设计元素
3. **一致性**：统一的交互模式和视觉语言
4. **响应性**：快速的用户反馈和流畅的动画
5. **可访问性**：支持键盘导航和屏幕阅读器

### 技术要求

1. 使用最新版本的依赖
2. TypeScript 严格模式
3. ESLint + Prettier 代码规范
4. 组件化开发，单一职责
5. Context 进行状态管理
6. 自定义 hooks 复用逻辑

### 样式指导

1. 优先使用 Tailwind 原生类
2. 必要时使用 CSS Variables
3. 响应式设计移动优先
4. 深色模式完整支持
5. 动画使用 Tailwind 或 CSS transitions

## 🚀 Demo 阶段计划

### Demo 1: 基础布局结构

- [x] 左右分栏布局
- [x] 侧边栏基础结构
- [x] 主聊天区基础结构
- [x] 主题切换功能

### Demo 2: 组件丰富化

- [ ] 消息气泡样式
- [x] 输入区域三层结构
- [x] 基础交互效果

### Demo 3: 完整功能

- 所有功能组件集成
- 完整交互流程
- 动画和优化

## 📊 当前进度总结 (更新于 2025-08-01)

### ✅ 已完成的核心功能

#### Phase 1: 项目基础 (100% 完成)

- ✅ 项目初始化和依赖安装完成
- ✅ 所有核心依赖包已安装 (React 19, Vite, Tailwind CSS, TypeScript)
- ✅ UI和功能依赖包完整 (@heroicons/react, axios, react-markdown, clsx等)
- ✅ Tailwind CSS主题系统配置完成，支持深色/浅色模式
- ✅ 基础目录结构已建立 (缺少 api、styles、utils 目录)

#### Phase 2: 核心架构 (90% 完成)

- ✅ ThemeContext 和 SidebarContext 状态管理完成
- ✅ 完整的类型定义系统 (User, Message, Conversation, API响应等)
- ✅ ConversationContext 对话管理完成
- ❌ UserContext 待创建
- ❌ API层基础结构待实现
- ❌ 样式工具函数待创建

#### Phase 3: 基础组件 (60% 完成)

- ✅ 布局组件全部完成 (MainLayout, Sidebar, ChatArea)
- ✅ Button 组件已实现 (支持多种变体)
- ✅ 主题切换功能完整实现
- ❌ 基础UI组件待完善 (Input, Avatar, Loading等)
- ❌ 用户状态组件待创建

### 🚧 当前开发阶段

**Demo 1 已完成**: 基础布局结构搭建完毕，具备：

- 完整的左右分栏响应式布局
- 功能完善的侧边栏 (支持折叠、移动端适配)
- 主聊天区域基础结构
- 完整的主题切换系统

**下一步重点**: 进入 Demo 2 阶段，已经完成：

1. ✅ 消息发送和接收功能
2. ✅ 三层输入区域结构
3. ✅ 基础交互效果和动画（键盘快捷键、加载状态）
4. ✅ 对话状态管理系统

**Demo 2 和第三阶段核心功能已完成！** 下一步进入高级功能开发：

1. ✅ 文件上传功能 - **第二阶段完成**
   - ✅ 完整的 FileUpload 组件 (支持拖拽和点击上传)
   - ✅ 文件类型和大小验证
   - ✅ 文件预览和删除功能
   - ✅ 粘贴文件支持 (图片和其他文件)
   - ✅ 与 ChatInput 集成

2. ✅ 工具栏功能 - **第三阶段完成**
   - ✅ 高级 ModelSelector 组件 (支持多种AI模型选择)
   - ✅ 键盘导航和无障碍支持
   - ✅ 模型状态管理和可用性检查
   - ✅ 美观的下拉界面和用户体验

3. ✅ 消息操作功能 - **第三阶段完成**
   - ✅ 复制消息到剪贴板 (兼容不同浏览器)
   - ✅ 用户消息编辑功能 (高级编辑模态框)
   - ✅ AI消息重新生成功能 (保持上下文)
   - ✅ 消息点赞/点踩功能 (视觉反馈)
   - ✅ 消息状态管理 (useMessageActions Hook)
   - ✅ 重新生成标记显示

4. [ ] 侧边栏对话列表
5. [ ] 高级UI组件完善

### 📋 优先级任务清单

1. **高优先级**: 创建 api、utils、styles 目录和基础文件
2. **高优先级**: 实现 UserContext 和 ConversationContext
3. **中优先级**: 完善 UI基础组件 (Input, Avatar, Loading)
4. **中优先级**: 实现消息相关组件 (MessageBubble, MessageActions)
5. **低优先级**: 高级功能 (文件上传、快捷键、动画)

# UI Code Structure Optimization TODO List

1. 拆分 ConversationContext.tsx 业务逻辑
   - [x] 将消息相关操作（如 sendMessage、editMessage、deleteMessage、regenerateMessage）拆分到 src/utils/conversationUtils.ts
   - [x] Context 只负责状态和接口暴露，复杂逻辑移至 utils/service 层
   - [x] 补充英文注释，提升可读性

2. 优化 MarkdownRenderer.tsx 结构
   - [x] 将 Mermaid 渲染相关逻辑单独提取为 MermaidChart.tsx，便于维护和复用
   - [x] 保持 MarkdownRenderer 只负责 markdown 渲染和组件组合

3. 组件分层与职责清晰
   - [x] 检查 src/components 目录下所有组件，确保 UI 组件只负责渲染和交互，业务逻辑不混杂（已完成，所有 UI 组件已归类至 src/components/ui，业务逻辑已抽离）
   - [x] 通用 UI 组件（如按钮、弹窗）与业务组件分开（已完成，Button、Modal、Tooltip、Avatar、Input 均在 src/components/ui）

4. 方法长度与复杂度优化
   - [x] 拆分长方法，每个函数只做一件事（已在 MarkdownRenderer、MermaidChart、CodeBlock 等关键组件实现）
   - [x] 对复杂分支和副作用（如 setTimeout、setState）加详细注释（已在主组件实现）

5. 目录结构与命名规范
   - [x] 检查并优化 src/utils/ 目录，集中消息、对话相关工具函数
   - [x] 检查并优化 src/hooks/ 目录，确保 hooks 只负责数据和状态，复杂逻辑拆分到 utils

6. 样式与语义化优化
   - [x] 检查 src/styles/index.css，确保样式按模块分组，命名语义化（已完成初步分组，后续可持续优化）
   - [x] 组件样式使用 Tailwind 组合式写法，避免原生 CSS（主流组件已实现）

7. 注释与文档
   - [x] 补充英文注释，特别是复杂逻辑和副作用部分（主组件已补充）
   - [x] 保持 README.md 与实际代码结构一致（已同步主要结构）

8. 测试覆盖
   - [x] 检查 src/__tests__/ 目录，补充关键方法和组件的单元测试（已补充 Button、Input、Modal、Tooltip、mockAI 基础测试）
