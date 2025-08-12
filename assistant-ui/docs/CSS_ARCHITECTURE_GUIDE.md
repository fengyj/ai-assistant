# CSS架构设计指南

## 📖 概述

本指南为前端项目建立了完整的CSS架构标准，旨在确保样式代码的可维护性、可扩展性和团队协作效率。本文档面向开发者和AI编程助手，提供系统性的架构原则和实践指导。

## 🎯 设计原则

### 核心原则

1. **模块化分离** - 样式按功能和组件分离到独立文件
2. **语义化优先** - 使用有意义的类名替代复杂的原子类组合
3. **渐进增强** - 先基础样式，再增强交互效果
4. **响应式设计** - 移动优先，逐步增强桌面体验
5. **主题兼容** - 支持深色/浅色主题切换
6. **性能导向** - 最小化CSS体积，优化加载速度

### SOLID原则在CSS中的应用

- **单一职责** - 每个CSS类只负责一个特定的样式功能
- **开闭原则** - CSS模块对扩展开放，对修改封闭
- **里氏替换** - 语义化类可以在不同上下文中互换使用
- **接口隔离** - 将复杂样式分解为多个简单的语义化类
- **依赖倒置** - 组件依赖抽象的样式类，而非具体的实现

## 🏗 文件结构规范

### 目录结构

```text
src/styles/
├── index.css                    # 入口文件 - 导入所有样式模块
├── base.css                     # 基础样式 - 重置、字体、颜色变量
├── layout.css                   # 布局样式 - 网格、容器、定位
├── utilities.css                # 工具类 - 间距、对齐、显示状态
├── animations.css               # 动画效果 - 过渡、关键帧、交互动画
└── components/                  # 组件样式目录
    ├── buttons.css              # 按钮组件样式
    ├── inputs.css               # 表单输入组件样式  
    ├── modals.css               # 模态框组件样式
    ├── navigation.css           # 导航组件样式
    ├── cards.css                # 卡片组件样式
    ├── tooltips.css             # 提示框组件样式
    ├── feedback.css             # 反馈组件样式(通知、警告等)
    └── [component-name].css     # 其他组件专用样式
```

### 文件命名约定

- **kebab-case** - 所有文件名使用短横线命名
- **语义明确** - 文件名要明确表达其包含的样式内容
- **避免缩写** - 使用完整单词，提高可读性

## 🎨 语义化类命名规范

### 命名方法论：BEM + 语义化

采用 **BEM (Block Element Modifier)** 方法论结合语义化命名：

- **Block** - 独立的功能块：`.btn-base`、`.modal-overlay`、`.tooltip-content`
- **Element** - 块内的元素：`.btn__icon`、`.modal__header`、`.tooltip__arrow`
- **Modifier** - 块或元素的变体：`.btn--primary`、`.btn--large`、`.modal--fullscreen`

### 类名分类体系

#### 1. 布局类 (Layout Classes)

负责页面整体布局和容器结构，如居中容器、网格布局、侧边栏布局等。

#### 2. 组件类 (Component Classes)

针对具体UI组件的样式，如按钮、输入框、模态框、提示框等。

#### 3. 状态类 (State Classes)

表示元素的交互状态，如加载中、禁用、激活、隐藏等状态。

#### 4. 工具类 (Utility Classes)

提供通用的样式功能，如文本截断、平滑过渡、屏幕阅读器支持等。

### 业务特异性命名原则

#### 🎯 核心原则：避免过度泛化

类名应该反映其具体的业务用途，避免使用过于宽泛的命名，以防止不同业务场景下的样式冲突。

#### ✅ 推荐做法

```css
/* ✅ 好的做法 - 业务特异性命名 */
.chat-code-block-header { }     /* 聊天中的代码块头部 */
.mermaid-chart-container { }    /* Mermaid图表容器 */
.sidebar-nav-item { }           /* 侧边栏导航项 */
.model-selector-dropdown { }    /* 模型选择下拉框 */
.message-edit-modal { }         /* 消息编辑模态框 */
```

#### ❌ 避免的做法

```css
/* ❌ 避免 - 过于泛化的命名 */
.header { }                     /* 太宽泛，可能用于多种头部 */
.container { }                  /* 太通用，容易冲突 */
.dropdown { }                   /* 没有业务上下文 */
.modal { }                      /* 缺乏具体用途说明 */
.button { }                     /* 过于基础 */
```

#### 📏 命名特异性级别

1. **通用基础类** - 仅用于真正的基础样式
   - `.btn-base`、`.input-base`、`.modal-overlay`

2. **功能特异类** - 包含功能上下文
   - `.auth-login-form`、`.user-profile-card`、`.settings-panel`

3. **业务特异类** - 包含完整业务上下文
   - `.chat-message-bubble`、`.model-config-modal`、`.file-upload-area`

#### 🔍 判断标准

在命名时问自己：

- 这个样式是否只在特定业务场景中使用？
- 是否可能与其他功能模块的样式冲突？
- 名称是否清楚表达了其具体用途？

如果答案是"是"、"是"、"是"，则应该使用更具体的业务特异性命名。

## 🚀 最佳实践

### ✅ 推荐的实现方式

#### 1. 组合语义化类

```tsx
// ✅ 好的做法 - 使用语义化类组合
<button className="btn-base btn-primary">
  提交
</button>

<div className="modal-overlay">
  <div className="modal-content centered-container">
    内容
  </div>
</div>
```

#### 2. 主题兼容设计

```css
/* ✅ 好的做法 - 使用CSS变量实现主题 */
.btn-primary {
  background-color: var(--color-primary);
  color: var(--color-primary-text);
  border-color: var(--color-primary-border);
}

:root {
  --color-primary: #3b82f6;
  --color-primary-text: white;
}

.dark {
  --color-primary: #60a5fa;
  --color-primary-text: #1e293b;
}
```

#### 3. 响应式设计模式

```css
/* ✅ 好的做法 - 移动优先的响应式设计 */
.grid-responsive {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1rem;
}

@media (min-width: 768px) {
  .grid-responsive {
    grid-template-columns: repeat(2, 1fr);
    gap: 1.5rem;
  }
}
```

#### 4. 渐进增强的交互效果

```css
/* ✅ 好的做法 - 基础样式 + 交互增强 */
.btn-base {
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  transition: all 0.2s ease-in-out;
  cursor: pointer;
}

.btn-base:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}
```

#### 5. 统一图标使用

```tsx
// ✅ 好的做法 - 使用系统图标库
import { CheckIcon, XMarkIcon, PlusIcon } from '@heroicons/react/24/outline'
import { Check, X, Plus } from 'lucide-react'

<button className="btn-primary">
  <PlusIcon className="btn__icon" />
  添加项目
</button>

<div className="success-message">
  <Check className="message__icon" />
  操作成功
</div>
```

### ❌ 应该避免的做法

#### 1. 避免超长的Tailwind类组合

```tsx
// ❌ 避免 - 复杂的原子类堆叠
<div className="absolute left-1/2 -translate-x-1/2 bottom-full mb-2 px-2 py-1 text-xs bg-gray-800 text-white rounded opacity-0 group-hover:opacity-100 transition pointer-events-none whitespace-nowrap z-10">
  提示内容
</div>

// ✅ 推荐 - 使用语义化类
<div className="tooltip-content">
  提示内容
</div>
```

#### 2. 避免内联样式

```tsx
// ❌ 避免 - 内联样式
<div style={{ 
  display: 'flex', 
  alignItems: 'center', 
  justifyContent: 'center',
  padding: '1rem',
  backgroundColor: '#f3f4f6'
}}>
  内容
</div>

// ✅ 推荐 - CSS类
<div className="centered-container">
  内容
</div>
```

#### 3. 避免深层嵌套选择器

```css
/* ❌ 避免 - 深层嵌套 */
.sidebar .nav .item .link .icon {
  color: #666;
}

/* ✅ 推荐 - 扁平化语义类 */
.nav-icon {
  color: var(--color-text-secondary);
}
```

#### 4. 避免硬编码值

```css
/* ❌ 避免 - 硬编码颜色和尺寸 */
.custom-button {
  background-color: #3b82f6;
  padding: 8px 16px;
  font-size: 14px;
}

/* ✅ 推荐 - 使用设计系统变量 */
.btn-primary {
  background-color: var(--color-primary);
  padding: var(--spacing-2) var(--spacing-4);
  font-size: var(--text-sm);
}
```

#### 5. 避免自定义SVG图标

```tsx
// ❌ 避免 - 自定义内联SVG图标
<button className="btn-primary">
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
    <path d="M12 5v14m-7-7h14" stroke="currentColor" strokeWidth="2"/>
  </svg>
  添加项目
</button>

// ❌ 避免 - 复杂的SVG组件实现
const CustomCheckIcon = () => (
  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
  </svg>
)

// ✅ 推荐 - 使用系统图标库
import { Check } from 'lucide-react'
<Check className="success-icon" />
```

## 🔧 工具和自动化

### CSS质量检测

项目配备自动化分析脚本 `scripts/analyze-styles.sh`，提供：

- 内联样式检测
- 复杂类组合识别
- CSS模块化分析
- 语义化类使用率评估
- 样式质量评分

### 构建时检查

建议在构建流程中集成CSS检查工具：

- **Stylelint** - CSS代码规范检查
- **PostCSS** - CSS预处理和优化
- **PurgeCSS** - 移除未使用的CSS

## 🎨 设计系统集成

### 变量系统规范

建立统一的设计令牌系统：

```css
/* 颜色系统示例 */
:root {
  /* 主色调 */
  --color-primary: #3b82f6;
  --color-primary-hover: #2563eb;
  
  /* 语义颜色 */
  --color-success: #10b981;
  --color-warning: #f59e0b;
  --color-error: #ef4444;
  
  /* 文本颜色 */
  --color-text-primary: #111827;
  --color-text-secondary: #6b7280;
  
  /* 背景颜色 */
  --color-bg-primary: #ffffff;
  --color-bg-secondary: #f9fafb;
}

/* 间距系统示例 */
:root {
  --spacing-1: 0.25rem;   /* 4px */
  --spacing-2: 0.5rem;    /* 8px */
  --spacing-3: 0.75rem;   /* 12px */
  --spacing-4: 1rem;      /* 16px */
  --spacing-6: 1.5rem;    /* 24px */
  --spacing-8: 2rem;      /* 32px */
}

/* 字体系统示例 */
:root {
  --text-xs: 0.75rem;     /* 12px */
  --text-sm: 0.875rem;    /* 14px */
  --text-base: 1rem;      /* 16px */
  --text-lg: 1.125rem;    /* 18px */
  
  --font-weight-normal: 400;
  --font-weight-medium: 500;
  --font-weight-semibold: 600;
}
```

### 主题系统

实现完整的主题切换支持：

```css
/* 默认浅色主题 */
:root {
  --color-bg-primary: #ffffff;
  --color-text-primary: #0f172a;
  --color-border: #e2e8f0;
}

/* 深色主题 */
.dark {
  --color-bg-primary: #0f172a;
  --color-text-primary: #f8fafc;
  --color-border: #334155;
}

/* 系统主题自动切换 */
@media (prefers-color-scheme: dark) {
  :root:not(.light) {
    --color-bg-primary: #0f172a;
    --color-text-primary: #f8fafc;
    --color-border: #334155;
  }
}
```

## 📱 响应式设计指南

### 断点策略

采用移动优先策略，定义清晰的断点系统：

- 手机：默认样式
- 平板：768px+
- 桌面：1024px+
- 大屏：1280px+

### 响应式模式

- **流式网格** - 使用CSS Grid实现自适应布局
- **弹性容器** - 容器宽度和间距的响应式调整
- **内容优先** - 确保内容在所有设备上的可读性

## 🔄 代码质量和维护

### 质量标准

- **性能指标** - CSS包大小控制在合理范围
- **可维护性** - 代码模块化程度和语义化率
- **兼容性** - 浏览器兼容性和主题适配
- **可访问性** - 无障碍设计规范遵循

### 重构指导

1. **识别问题** - 使用自动化工具识别代码异味
2. **制定计划** - 按优先级规划重构任务
3. **渐进改进** - 小步快跑，避免大规模重写
4. **验证效果** - 确保重构后功能和视觉的一致性

## 💡 AI编程助手指导原则

### 系统级指令

当AI编程助手（如GitHub Copilot、Claude等）协助CSS开发时，应遵循以下原则：

#### 架构设计原则

- 优先考虑模块化和可维护性
- 始终使用语义化类名替代复杂原子类组合
- **强制业务特异性命名** - 避免使用过于宽泛的类名，必须包含业务上下文
- 确保所有样式支持深色/浅色主题
- 遵循移动优先的响应式设计策略
- 使用设计系统变量而非硬编码值

#### 业务特异性命名检查

AI助手在生成CSS类名时必须检查：

- **上下文识别** - 分析组件所属的业务模块（chat、auth、model、sidebar等）
- **用途明确性** - 类名是否清楚表达具体用途而非泛化概念
- **冲突避免** - 确保不会与其他业务模块的样式产生命名冲突
- **团队理解性** - 类名是否便于团队成员快速理解和维护

#### 代码质量检查

- 检测并标记超过8个类的复杂组合
- 识别内联样式使用并建议替代方案
- 发现重复的样式模式并建议抽象
- 验证CSS变量的正确使用
- 确保无障碍设计规范的遵循

#### 重构策略

- 分析现有代码的复杂度和重复性
- 提供渐进式重构建议
- 优先处理高影响、低风险的改进
- 保持视觉效果的一致性
- 提供重构前后的质量对比

#### 命名约定

- 使用BEM方法论结合语义化命名
- **强制包含业务上下文** - 类名必须反映具体业务场景
- 确保类名的可读性和描述性
- 避免缩写和模糊的命名
- 保持命名的一致性和可预测性

#### 性能优化

- 最小化CSS选择器的复杂度
- 优化关键渲染路径
- 合理使用CSS动画和过渡
- 控制CSS包的大小和加载性能

#### 图标使用规范

- **统一图标库** - 始终使用项目指定的图标库（如Lucide React、Heroicons等）
- **避免自定义SVG** - 不要自行实现SVG图标，使用系统统一的图标组件
- **保持一致性** - 确保图标风格、大小和语义的一致性
- **性能考虑** - 图标库通常经过优化，比自定义SVG有更好的加载性能

### 协作模式

#### 系统提示词（用于AI编程助手配置）

```text
你是一个专业的CSS架构师和前端开发专家。当协助用户进行CSS相关开发时，必须严格遵循以下规范：

## 核心规则（必须遵守）

1. **禁止使用超过6个类的复杂组合**
   - 检测到超过6个Tailwind类的组合时，必须建议创建语义化CSS类
   - 示例：将 className="flex items-center justify-center p-4 bg-blue-500 text-white rounded-lg shadow-lg hover:bg-blue-600 transition-colors" 重构为 className="btn-primary"

2. **强制使用业务特异性语义化类名**
   - 按钮组件：使用 chat-send-btn、auth-login-btn、model-config-btn 等
   - 布局容器：使用 chat-message-container、sidebar-nav-container 等
   - 状态类：使用 message-loading-state、file-upload-error-state 等
   - 禁止直接在JSX中使用长串原子类
   - **严禁使用过于宽泛的类名**：如 .header、.container、.button 等

3. **业务上下文强制检查**
   - 每个类名必须包含业务模块信息（chat、auth、model、sidebar、file、message等）
   - 类名必须明确表达具体用途而非泛化概念
   - 必须避免与其他业务模块的样式产生命名冲突

4. **主题兼容性检查**
   - 任何颜色相关的CSS必须使用CSS变量：var(--color-primary) 而非 #3b82f6
   - 检查深色主题兼容性，确保定义了 .dark 选择器下的变量

5. **响应式设计强制要求**
   - 所有布局必须采用移动优先策略
   - 断点使用：默认（手机）→ @media (min-width: 768px)（平板）→ @media (min-width: 1024px)（桌面）

6. **图标使用严格规范**
   - 检测到SVG内联代码时，必须建议使用图标库（Lucide React、Heroicons）
   - 示例：将 <svg>...</svg> 替换为 <Check className="icon-sm" />

## 代码生成规则

当生成CSS代码时：

1. **文件结构遵循**
   - 组件样式 → src/styles/components/[component].css
   - 基础样式 → src/styles/base.css
   - 布局样式 → src/styles/layout.css
   - 工具类 → src/styles/utilities.css

2. **类命名规范**
   /* 正确：BEM + 业务特异性语义化 */
   .chat-message-bubble { }
   .chat-message__avatar { }
   .chat-message--user { }
   .model-selector-dropdown { }
   .auth-login-form { }

   /* 错误：避免这样命名 */
   .button1 { }
   .header { }
   .container { }
   .dropdown { }

3. **CSS变量系统**
   /* 必须使用设计系统变量 */
   .chat-send-btn {
     background-color: var(--color-primary);
     color: var(--color-primary-text);
     padding: var(--spacing-2) var(--spacing-4);
     font-size: var(--text-sm);
   }

## 代码审查检查点

在提供代码建议时，自动检查：

- ✅ 是否使用了业务特异性语义化类名
- ✅ 是否避免了超长类组合
- ✅ 是否使用CSS变量而非硬编码值
- ✅ 是否支持深色主题
- ✅ 是否采用移动优先设计
- ✅ 是否使用了系统图标库
- ✅ 是否考虑了无障碍性（aria属性、对比度）
- ✅ 类名是否包含明确的业务上下文

## 重构建议格式

当发现不规范代码时，按此格式提供建议：

❌ 当前代码问题：
[具体指出问题，特别是命名过于宽泛的问题]

✅ 建议的改进方案：
[提供具体的重构代码，确保类名包含业务上下文]

📝 改进理由：
[解释为什么这样改进，强调业务特异性的重要性]

🎯 架构影响：
[说明对整体架构的积极影响]

## 性能优化检查

- 检查CSS选择器深度（不超过3层）
- 建议使用 transform 和 opacity 实现动画
- 识别重复样式并建议抽象为公共类
- 检查CSS包大小影响

## 错误处理

遇到以下情况必须警告：
- 内联样式使用
- 硬编码颜色值
- 深层嵌套选择器（超过3层）
- **过于宽泛的类名**（如 .header、.container、.button 等）
- 缺少业务上下文的类名
- 缺少响应式设计
- 自定义SVG图标

遵循这些规则，确保生成的CSS代码符合项目架构标准，具有良好的可维护性和扩展性，并严格遵循业务特异性命名原则。
```

#### 实际协作流程

AI助手在实际工作中应该：

1. **代码分析阶段**
   - 扫描现有代码中的CSS类使用模式
   - 识别不符合规范的代码片段
   - **特别检查类名的业务特异性**
   - 评估代码的架构合规性

2. **建议生成阶段**
   - 提供具体的重构代码示例
   - **确保所有类名包含业务上下文**
   - 解释每个改进的架构理由
   - 给出渐进式改进方案

3. **质量验证阶段**
   - 确保建议的代码符合所有架构原则
   - **验证类名的业务特异性和唯一性**
   - 验证主题兼容性和响应式效果
   - 检查无障碍性和性能影响

## 📋 检查清单

### 开发阶段检查

- [ ] 使用业务特异性语义化类名而非复杂原子类组合
- [ ] 类名包含明确的业务上下文信息
- [ ] 实现移动优先的响应式设计
- [ ] 支持深色/浅色主题切换
- [ ] 使用CSS变量而非硬编码值
- [ ] 考虑无障碍访问需求
- [ ] 优化动画性能（使用transform和opacity）
- [ ] 使用系统图标库而非自定义SVG图标

### 代码审查检查

- [ ] 遵循项目设计系统规范
- [ ] 类名具有业务特异性，避免过于宽泛
- [ ] 清理不再使用的样式代码
- [ ] 运行样式分析脚本验证质量
- [ ] 测试不同屏幕尺寸的显示效果
- [ ] 验证主题切换的正确性
- [ ] 确保无障碍标准的遵循
- [ ] 检查图标使用的一致性和标准化

---

*本指南作为项目CSS开发的核心标准，所有样式相关的开发和重构都应参考此文档。特别注意类名的业务特异性原则，避免使用过于宽泛的命名方式。*
