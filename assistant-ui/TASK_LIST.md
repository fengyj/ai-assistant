# AI Assistant UI 重构任务列表

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
- [ ] 备份现有代码
- [ ] 清理 assistant-ui 目录
- [ ] 重新初始化 Vite + React + TypeScript 项目

#### 1.2 安装核心依赖
- [ ] React 19 + TypeScript
- [ ] Vite (最新版本)
- [ ] Tailwind CSS (最新版本)
- [ ] PostCSS + Autoprefixer

#### 1.3 安装UI相关依赖
- [ ] @heroicons/react (图标库)
- [ ] react-intl (国际化)
- [ ] clsx (条件样式工具)

#### 1.4 安装功能依赖
- [ ] axios (API 请求)
- [ ] react-markdown (Markdown 渲染)
- [ ] prism-react-renderer (代码高亮)
- [ ] mermaid (图表渲染)
- [ ] react-dropzone (文件上传)

#### 1.5 配置Tailwind CSS主题系统
- [ ] 配置 dark/light 模式
- [ ] 定义自定义颜色变量
- [ ] 设置紧凑间距系统
- [ ] 配置自定义动画

#### 1.6 设置基础目录结构
- [ ] 创建 src/components/ 目录
- [ ] 创建 src/pages/ 目录
- [ ] 创建 src/api/ 目录
- [ ] 创建 src/context/ 目录
- [ ] 创建 src/styles/ 目录
- [ ] 创建 src/types/ 目录
- [ ] 创建 src/utils/ 目录
- [ ] 创建 src/hooks/ 目录

### Phase 2: 核心架构搭建

#### 2.1 创建Context状态管理系统
- [ ] ThemeContext (主题切换)
- [ ] UserContext (用户状态)
- [ ] ConversationContext (对话管理)
- [ ] UIContext (界面状态，如侧边栏折叠)

#### 2.2 创建基础类型定义
- [ ] User 类型
- [ ] Message 类型
- [ ] Conversation 类型
- [ ] Theme 类型
- [ ] API 响应类型

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
- [ ] MainLayout (主布局组件)
- [ ] Sidebar (侧边栏布局)
- [ ] ChatArea (聊天区域布局)

#### 3.2 UI基础组件
- [ ] Button (多种变体：primary, secondary, icon)
- [ ] Input (多行输入框)
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
- [ ] MessageActions (消息操作按钮)
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
- [ ] ChatInput (三层输入区域)
- [ ] FileUpload (文件上传区域)
- [ ] InputTextarea (多行输入框)
- [ ] Toolbar (工具栏)
- [ ] ModelSelector (模型选择)
- [ ] TokenStats (token统计)
- [ ] NotificationIcon (通知图标)

### Phase 5: 页面整合与优化

#### 5.1 主页面组件整合
- [ ] ChatPage (聊天主页面)
- [ ] 组件间数据流
- [ ] 事件处理机制

#### 5.2 响应式布局优化
- [ ] 移动端适配
- [ ] 平板端适配
- [ ] 大屏幕优化

#### 5.3 交互动画添加
- [ ] 页面切换动画
- [ ] 消息发送动画
- [ ] 悬停效果
- [ ] 加载状态动画

#### 5.4 无障碍功能完善
- [ ] ARIA 标签
- [ ] 键盘导航
- [ ] 屏幕阅读器支持
- [ ] 焦点管理

### Phase 6: 功能特性实现

#### 6.1 文件处理
- [ ] 拖拽上传
- [ ] 粘贴上传
- [ ] 文件预览
- [ ] 文件删除

#### 6.2 键盘快捷键
- [ ] Ctrl+Enter 发送
- [ ] 其他快捷键支持

#### 6.3 消息操作
- [ ] 复制消息
- [ ] 编辑消息
- [ ] 重新生成
- [ ] 点赞/点踩

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

- 消息气泡样式
- 输入区域三层结构
- 基础交互效果

### Demo 3: 完整功能

- 所有功能组件集成
- 完整交互流程
- 动画和优化
