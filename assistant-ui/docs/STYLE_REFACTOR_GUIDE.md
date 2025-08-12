# 样式重构实施指南

## 重构前审查命令

### 1. 统计内联样式数量
```bash
# 搜索所有内联样式
grep -r "style={{" src/ --include="*.tsx" --include="*.ts" -n

# 统计内联样式总数
grep -r "style={{" src/ --include="*.tsx" --include="*.ts" | wc -l
```

### 2. 分析Tailwind原子类堆叠
```bash
# 搜索包含多个Tailwind类的长className
grep -r "className.*=.*[\"'][^\"']*flex.*[\"']" src/ --include="*.tsx" -n | head -20

# 搜索特定模式的重复样式
grep -r "flex flex-col" src/ --include="*.tsx" -n
grep -r "items-center justify-center" src/ --include="*.tsx" -n
grep -r "bg-white dark:bg-gray" src/ --include="*.tsx" -n
```

### 3. 统计CSS文件大小和复杂度
```bash
# 统计主样式文件行数
wc -l src/styles/index.css

# 查看样式文件结构
find src/styles/ -name "*.css" -exec wc -l {} \;
```

## 重构实施工具

### 语义化类名映射表示例

| 原Tailwind组合 | 语义化类名 | 用途 |
|---|---|---|
| `flex flex-col h-full` | `.main-layout` | 主要布局容器 |
| `items-center justify-center min-h-screen` | `.centered-container` | 居中容器 |
| `bg-white dark:bg-gray-800 border-gray-200` | `.card` | 卡片组件 |
| `p-2 text-gray-600 hover:text-gray-800 rounded-lg` | `.btn-icon` | 图标按钮 |
| `w-full p-3 border border-gray-300 rounded-md` | `.form-input` | 表单输入框 |

### 批量查找替换示例

```bash
# 查找需要抽象的重复模式
grep -r "flex flex-col h-full" src/ --include="*.tsx" -l

# 查找内联样式文件
grep -r "style={{" src/ --include="*.tsx" -l
```

## 质量验证检查单

### 代码层面验证
- [ ] 运行 `grep -r "style={{" src/ --include="*.tsx"` 确认无内联样式
- [ ] 运行 `npm run lint` 确保代码规范
- [ ] 运行 `npm run build` 确保构建成功

### 视觉验证
- [ ] 启动开发服务器：`npm run dev`
- [ ] 测试主页面渲染正常
- [ ] 测试深色/浅色主题切换
- [ ] 测试移动端响应式布局
- [ ] 测试所有交互功能（按钮、输入框、模态框等）

### 性能验证
- [ ] 检查CSS文件大小是否合理
- [ ] 确认没有未使用的CSS规则
- [ ] 验证样式加载性能

## 回滚计划

如果重构出现问题：

1. **保存当前状态**：`git stash`
2. **回滚到上一个提交**：`git reset --hard HEAD~1`
3. **重新开始小步骤重构**

## 样式文件结构检查

期望的最终文件结构：
```
src/styles/
├── index.css          # 入口文件，导入其他样式
├── base.css           # 基础样式、重置、全局变量
├── layout.css         # 布局相关样式
├── components/
│   ├── button.css     # 按钮样式
│   ├── input.css      # 输入框样式
│   ├── chat.css       # 聊天相关样式
│   ├── sidebar.css    # 侧边栏样式
│   ├── markdown.css   # Markdown渲染样式
│   ├── model-selector.css  # 模型选择器样式
│   └── file-upload.css     # 文件上传样式
└── utilities.css      # 工具类样式
```
