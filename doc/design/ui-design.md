# UI Design

The frontend is a single page application.

## Overall Layout

The main interface adopts a two-column layout:

- **Left Sidebar**: Displays conversation history and navigation.
- **Right Main Area**: Shows the current chat session, message list, and input area.

Below is a schematic layout (for illustration):

```html
<!-- UI Layout Schematic -->
<div class="chat-layout-root">
  <aside class="sidebar-nav-container">
    <!-- Conversation history, user info, navigation -->
  </aside>
  <main class="chat-main-panel">
    <header class="chat-header-bar">
      <!-- Current conversation title, settings icon -->
    </header>
    <section class="chat-message-container">
      <!-- Chat messages will appear here -->
    </section>
    <footer class="chat-input-panel">
      <!-- Message input box, send button, file upload, model selector -->
    </footer>
  </main>
  <aside class="chat-preview-panel">
    <!-- Preview of code, markdown, or AI output -->
  </aside>
</div>
```

## Color Scheme

The color system is fully managed by CSS variables, defined in the project's base CSS files (see `src/styles/base.css`). All color-related styles must use these variables to ensure theme consistency and easy switching.

### Main Color Variables and Usage

| Variable            | Usage                        | Light      | Dark       |
|---------------------|-----------------------------|------------|------------|
| `--color-bg-primary`    | 主背景、主容器              | <span style="display:inline-block;width:14px;height:14px;background:#f8fafc;border-radius:3px;vertical-align:middle;margin-right:4px;"></span>#f8fafc  | <span style="display:inline-block;width:14px;height:14px;background:#18181b;border-radius:3px;vertical-align:middle;margin-right:4px;"></span>#18181b  |
| `--color-bg-secondary`  | 侧边栏、输入区、卡片        | <span style="display:inline-block;width:14px;height:14px;background:#f1f5f9;border-radius:3px;vertical-align:middle;margin-right:4px;"></span>#f1f5f9  | <span style="display:inline-block;width:14px;height:14px;background:#23272f;border-radius:3px;vertical-align:middle;margin-right:4px;"></span>#23272f  |
| `--color-bg-accent`     | 高亮区、选中态              | <span style="display:inline-block;width:14px;height:14px;background:#e0e7ef;border-radius:3px;vertical-align:middle;margin-right:4px;"></span>#e0e7ef  | <span style="display:inline-block;width:14px;height:14px;background:#27272a;border-radius:3px;vertical-align:middle;margin-right:4px;"></span>#27272a  |
| `--color-text-primary`  | 主文本                     | <span style="display:inline-block;width:14px;height:14px;background:#1e293b;border-radius:3px;vertical-align:middle;margin-right:4px;"></span>#1e293b  | <span style="display:inline-block;width:14px;height:14px;background:#f1f5f9;border-radius:3px;vertical-align:middle;margin-right:4px;"></span>#f1f5f9  |
| `--color-text-secondary`| 辅助文本、标签              | <span style="display:inline-block;width:14px;height:14px;background:#64748b;border-radius:3px;vertical-align:middle;margin-right:4px;"></span>#64748b  | <span style="display:inline-block;width:14px;height:14px;background:#a1a1aa;border-radius:3px;vertical-align:middle;margin-right:4px;"></span>#a1a1aa  |
| `--color-primary`       | 品牌主色、按钮、链接        | <span style="display:inline-block;width:14px;height:14px;background:#3b82f6;border-radius:3px;vertical-align:middle;margin-right:4px;"></span>#3b82f6  | <span style="display:inline-block;width:14px;height:14px;background:#60a5fa;border-radius:3px;vertical-align:middle;margin-right:4px;"></span>#60a5fa  |
| `--color-primary-text`  | 主色上的文本                | <span style="display:inline-block;width:14px;height:14px;background:#fff;border:1px solid #e5e7eb;border-radius:3px;vertical-align:middle;margin-right:4px;"></span>#fff     | <span style="display:inline-block;width:14px;height:14px;background:#1e293b;border-radius:3px;vertical-align:middle;margin-right:4px;"></span>#1e293b  |
| `--color-border`        | 边框、分割线                | <span style="display:inline-block;width:14px;height:14px;background:#e5e7eb;border-radius:3px;vertical-align:middle;margin-right:4px;"></span>#e5e7eb  | <span style="display:inline-block;width:14px;height:14px;background:#27272a;border-radius:3px;vertical-align:middle;margin-right:4px;"></span>#27272a  |
| `--color-accent`        | 强调色、提示、高亮          | <span style="display:inline-block;width:14px;height:14px;background:#fbbf24;border-radius:3px;vertical-align:middle;margin-right:4px;"></span>#fbbf24  | <span style="display:inline-block;width:14px;height:14px;background:#fbbf24;border-radius:3px;vertical-align:middle;margin-right:4px;"></span>#fbbf24  |
| `--color-success`       | 成功状态                   | <span style="display:inline-block;width:14px;height:14px;background:#22c55e;border-radius:3px;vertical-align:middle;margin-right:4px;"></span>#22c55e  | <span style="display:inline-block;width:14px;height:14px;background:#22c55e;border-radius:3px;vertical-align:middle;margin-right:4px;"></span>#22c55e  |
| `--color-warning`       | 警告状态                   | <span style="display:inline-block;width:14px;height:14px;background:#f59e42;border-radius:3px;vertical-align:middle;margin-right:4px;"></span>#f59e42  | <span style="display:inline-block;width:14px;height:14px;background:#f59e42;border-radius:3px;vertical-align:middle;margin-right:4px;"></span>#f59e42  |
| `--color-error`         | 错误状态                   | <span style="display:inline-block;width:14px;height:14px;background:#ef4444;border-radius:3px;vertical-align:middle;margin-right:4px;"></span>#ef4444  | <span style="display:inline-block;width:14px;height:14px;background:#ef4444;border-radius:3px;vertical-align:middle;margin-right:4px;"></span>#ef4444  |
| `--color-disabled`      | 禁用控件                   | <span style="display:inline-block;width:14px;height:14px;background:#cbd5e1;border-radius:3px;vertical-align:middle;margin-right:4px;"></span>#cbd5e1  | <span style="display:inline-block;width:14px;height:14px;background:#52525b;border-radius:3px;vertical-align:middle;margin-right:4px;"></span>#52525b  |

> 具体变量定义详见 `/assistant-ui/src/styles/base.css`，所有组件样式必须通过这些变量引用颜色。

#### Usage Guidelines

- 页面和主容器背景：`--color-bg-primary`
- 侧边栏、输入区、卡片等：`--color-bg-secondary`
- 主要文本：`--color-text-primary`
- 辅助文本、标签：`--color-text-secondary`
- 主要按钮、操作：`--color-primary` + `--color-primary-text`
- 边框、分割线：`--color-border`
- 状态提示（成功/警告/错误）：`--color-success`、`--color-warning`、`--color-error`
- 禁用控件：`--color-disabled`

### Theme Switching

- **Dark Theme**:  
  - 通过 `.dark` 类切换，变量在 `.dark` 作用域下重定义
- **Light Theme**:  
  - 默认主题，变量定义在 `:root`

> 详见 `/assistant-ui/src/styles/base.css`、`/assistant-ui/src/styles/components/common.css` 等文件。

## Components

### Sidebar Component

- 位于页面左侧，支持展开/折叠两种状态。
- 顶部为一个三条横线的菜单图标（建议使用系统 icon 库如 Lucide React 的 `Menu` 图标），点击可切换 sidebar 展开/收起。
- 菜单图标右侧显示标题“对话历史”。
- 标题下方为会话分组列表，分组包括：今天、昨天、本周、本月、历史月份等，每组下为对应的会话项。
- 会话项以列表形式展示，支持 hover 高亮、选中态。
- 支持滚动，超出部分可滚动浏览。
- 底部为用户信息栏，显示当前用户头像、昵称及状态（如在线/离线），并包含设置/退出等操作按钮。
- sidebar 可响应式收缩，收起时仅显示图标，展开时显示完整内容。
- 所有配色、边框、hover 效果均通过 CSS 变量实现，兼容深色/浅色主题。
- 推荐所有 class 命名均带 sidebar 前缀，避免与其他模块样式冲突。
- 每个历史对话项（`.sidebar-conversation-item`）在 hover 时，右侧显示“更多操作”图标（建议使用 Lucide React 的 `MoreVertical` 图标）。
- 点击“更多操作”图标弹出菜单，包含：
  - `重命名`：可编辑当前会话名称。
  - `删除`：删除当前会话，需使用警示色（如背景 `var(--color-error)`，文字 `var(--color-primary-text)`），并在 hover/active 态下突出显示风险。
- 删除项需有二次确认弹窗，防止误操作。
- 所有菜单及交互按钮需保证无障碍（aria-label、键盘可达）。

### Chat Area Component

- 占据主区域，分为顶部栏、消息区、输入区三部分。
- **顶部栏**（`.chat-header-bar`）：
  - 左侧显示当前会话标题（支持重命名，hover 时出现编辑图标）。
  - 右侧为主题切换按钮（建议用 Lucide React 的 `Sun`/`Moon` 图标），以及展开/折叠preview panel按钮（`<`/`>` 图标）。
  - 顶部栏有底部分割线，风格简洁。
- **消息区**（`.chat-message-container`）：
  - 垂直滚动区域，自动填充剩余空间。
  - 消息以气泡形式展示，分为用户消息（右侧，`.chat-message-bubble--user`）和助手消息（左侧，`.chat-message-bubble--assistant`）。
  - 每条消息包含时间戳、消息内容。
  - 支持代码高亮、Markdown 渲染、图片/表格等富文本内容。
  - 用户消息和助手消息颜色区分，均用 CSS 变量控制，兼容深色/浅色主题。
  - 支持消息 hover 时显示操作按钮（如复制，助手的消息还有重新生成、赞、踩按钮，用户的消息里还有编辑按钮）。
  - 支持消息发送/生成时的 loading 态（`.message-loading-state`）。
- **输入区**（`.chat-input-panel`）：
  - 分为三层：
    1. 顶部为文件上传工具栏（`.file-upload-toolbar`），支持拖拽和点击上传，显示已上传文件列表。
    2. 中间为多行自适应高度输入框（`.chat-input-textarea`），支持粘贴图片/文件。
    3. 底部为工具栏（`.chat-input-toolbar`），包含模型选择器（`.model-selector-dropdown`）、模型状态、设置按钮（`.model-config-btn`）、发送按钮（`.chat-send-btn`）等。
  - 发送按钮位于最右侧，支持快捷键发送（如 Ctrl+Enter）。
  - 输入区整体有顶部边框，风格与消息区区分。
  - 所有按钮、输入框、文件列表等均用业务语义 class 命名，禁止使用通用 class。
- 所有交互按钮需有 aria-label，保证无障碍。
- 所有配色、边框、hover 效果均通过 CSS 变量实现，兼容深色/浅色主题。
- 移动端下输入区和消息区自适应，顶部栏可收起。

### Preview Panel Component

- Located on the right side of the main chat area.
- Used to preview code snippets, markdown rendering, or AI生成的内容（如表格、图片、富文本等）。
- 支持多种内容类型的渲染（如代码高亮、表格、图片、富文本等）。(PS: pdf文件可以考虑EmbedPdf)
- 可以根据当前聊天内容自动切换预览内容，也支持用户手动切换不同的预览模式。
- 典型交互包括：点击消息中的“预览”按钮，或自动在生成代码/表格时显示预览。
- 设计参考 Copilot Chat 的右侧预览区，保持简洁、可收缩、与主聊天区风格一致。
- 支持多tab显示，用于显示多个内容。比如一个tab显示模型的思考过程，另一个显示用户上传的PDF文件。用户可以点击tab上的关闭按钮关闭tab。
- Tab header位于panel上方，在右侧有菜单按钮（“更多操作”图标）。点击可列出所有可预览项目，已打开的项目可在菜单项上用合适的图标（比如`√`）表示状态。
- 每个tab，上方是工具栏，显示工具按钮，比如下载等。
- 支持拖拽tab排序，tab宽度自适应内容，超出时可横向滚动。
- Panel整体可通过右上角的收起/展开按钮隐藏或显示，收起后仅显示一个窄条和展开按钮。
- 内容区（`.chat-preview-content`）根据内容类型自适应布局，支持代码高亮、表格滚动、PDF预览、图片缩放等。
- 工具栏按钮需有 aria-label，保证无障碍。
- 所有配色、边框、hover 效果均通过 CSS 变量实现，兼容深色/浅色主题。
- 推荐所有 class 命名均带 chat-preview 前缀，避免与其他模块样式冲突。

**结构示意：**

```html
<aside class="chat-preview-panel">
  <div class="chat-preview-header">
    <div class="chat-preview-tabs">
      <!--
        <div class="chat-preview-tab chat-preview-tab--active">
          <span class="chat-preview-tab-title">Tab标题</span>
          <button class="chat-preview-tab-close" aria-label="关闭"></button>
        </div>
        ...更多tab...
      -->
    </div>
    <button class="chat-preview-tabs-menu" aria-label="更多预览项目"></button>
    <button class="chat-preview-panel-toggle" aria-label="收起/展开"></button>
  </div>
  <div class="chat-preview-toolbar">
    <!-- 工具按钮，如下载、复制、刷新等 -->
  </div>
  <div class="chat-preview-content">
    <!-- 动态渲染内容：代码、表格、图片、PDF等 -->
  </div>
</aside>
```
