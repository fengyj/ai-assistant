#!/bin/bash

# 样式重构分析脚本
# 用于分析当前项目的样式使用情况

echo "=== 前端样式重构分析报告 ==="
echo "分析时间: $(date)"
echo ""

# 1. 统计内联样式
echo "1. 内联样式统计:"
echo "--------------------"
inline_styles_count=$(grep -r "style={{" src/ --include="*.tsx" --include="*.ts" 2>/dev/null | wc -l)
echo "总计内联样式数量: $inline_styles_count"

if [ $inline_styles_count -gt 0 ]; then
    echo "内联样式文件分布:"
    grep -r "style={{" src/ --include="*.tsx" --include="*.ts" -l 2>/dev/null | sort | uniq -c
    echo ""
    echo "示例内联样式:"
    grep -r "style={{" src/ --include="*.tsx" --include="*.ts" -n 2>/dev/null | head -5
fi
echo ""

# 2. 统计Tailwind类堆叠
echo "2. Tailwind原子类堆叠分析:"
echo "-----------------------------"

echo "常见布局模式统计:"
flex_col_count=$(grep -r "flex flex-col" src/ --include="*.tsx" 2>/dev/null | wc -l)
center_count=$(grep -r "items-center justify-center" src/ --include="*.tsx" 2>/dev/null | wc -l)
bg_pattern_count=$(grep -r "bg-white dark:bg-gray" src/ --include="*.tsx" 2>/dev/null | wc -l)

echo "- 'flex flex-col' 使用次数: $flex_col_count"
echo "- 'items-center justify-center' 使用次数: $center_count"  
echo "- 'bg-white dark:bg-gray' 模式使用次数: $bg_pattern_count"
echo ""

# 3. CSS文件分析
echo "3. CSS文件分析:"
echo "----------------"
if [ -f "src/styles/index.css" ]; then
    main_css_lines=$(wc -l < src/styles/index.css)
    echo "主样式文件 (src/styles/index.css) 行数: $main_css_lines"
else
    echo "未找到主样式文件 src/styles/index.css"
fi

echo "所有CSS文件:"
find src/ -name "*.css" -exec wc -l {} \; 2>/dev/null | sort -nr
echo ""

# 4. 组件文件统计
echo "4. 组件文件统计:"
echo "----------------"
tsx_files_count=$(find src/ -name "*.tsx" | wc -l)
ts_files_count=$(find src/ -name "*.ts" | wc -l)
echo "TypeScript React组件文件 (.tsx): $tsx_files_count"
echo "TypeScript文件 (.ts): $ts_files_count"
echo ""

# 5. 重构优先级建议
echo "5. 重构优先级建议:"
echo "-------------------"

if [ $inline_styles_count -gt 10 ]; then
    echo "🔴 高优先级: 内联样式过多 ($inline_styles_count 处)，需要立即处理"
elif [ $inline_styles_count -gt 0 ]; then
    echo "🟡 中优先级: 存在少量内联样式 ($inline_styles_count 处)"
else
    echo "✅ 无内联样式问题"
fi

if [ $main_css_lines -gt 500 ]; then
    echo "🔴 高优先级: 主CSS文件过大 ($main_css_lines 行)，需要拆分"
elif [ $main_css_lines -gt 300 ]; then
    echo "🟡 中优先级: 主CSS文件较大 ($main_css_lines 行)，建议拆分"
else
    echo "✅ CSS文件大小合理"
fi

if [ $flex_col_count -gt 5 ] || [ $center_count -gt 3 ]; then
    echo "🟡 中优先级: 发现重复的Tailwind类组合，建议抽象为语义化类"
fi

echo ""
echo "=== 分析完成 ==="
echo "建议按照 CSS_REFACTOR_TASK_LIST.md 中的步骤进行重构"
