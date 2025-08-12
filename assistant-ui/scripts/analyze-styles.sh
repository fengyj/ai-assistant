#!/bin/bash

# 全面样式分析脚本 - 合并版本
# 用于检测和分析前端项目的样式质量问题
# 支持内联样式检测、复杂Tailwind类组合检测、模式识别等功能

echo "=== 前端样式质量分析报告 ==="
echo "分析时间: $(date)"
echo "项目路径: $(pwd)"
echo ""

# 1. 内联样式统计与检测
echo "1. 内联样式统计:"
echo "--------------------"
inline_styles_count=$(grep -r "style={{" src/ --include="*.tsx" --include="*.ts" 2>/dev/null | wc -l)
echo "总计内联样式数量: $inline_styles_count"

if [ $inline_styles_count -gt 0 ]; then
    echo ""
    echo "内联样式文件分布:"
    grep -r "style={{" src/ --include="*.tsx" --include="*.ts" -l 2>/dev/null | sort | uniq -c | \
      awk '{printf "  %s 处 - %s\n", $1, $2}'
    
    echo ""
    echo "详细内联样式列表:"
    grep -r "style={{" src/ --include="*.tsx" --include="*.ts" -n 2>/dev/null | \
      sed 's/style={{/\n      → style={{/g' | head -10
fi
echo ""

# 2. 复杂Tailwind类组合检测（增强版）
echo "2. 复杂Tailwind类组合分析:"
echo "-----------------------------"

# 统计常见重复模式
echo "常见重复模式统计:"
flex_col_count=$(grep -r "flex flex-col" src/ --include="*.tsx" 2>/dev/null | wc -l)
center_count=$(grep -r "items-center justify-center" src/ --include="*.tsx" 2>/dev/null | wc -l)
bg_pattern_count=$(grep -r "bg-white dark:bg-gray" src/ --include="*.tsx" 2>/dev/null | wc -l)
spacing_pattern=$(grep -r "px-[0-9] py-[0-9]" src/ --include="*.tsx" 2>/dev/null | wc -l)

echo "  - 'flex flex-col' 重复使用: $flex_col_count 次"
echo "  - 'items-center justify-center' 重复使用: $center_count 次"  
echo "  - 'bg-white dark:bg-gray*' 主题模式: $bg_pattern_count 次"
echo "  - 'px-* py-*' 间距模式: $spacing_pattern 次"

# 检测超长类组合（8个以上类）
echo ""
echo "超长类组合检测 (8+ 类):"
complex_classnames=$(grep -r 'className="[^"]*"' src/ --include="*.tsx" 2>/dev/null | \
  awk -F'className="' '{print $2}' | \
  awk -F'"' '{print $1}' | \
  awk '{if(NF >= 8) print}' | \
  wc -l)

echo "  发现超长类组合数量: $complex_classnames"

if [ $complex_classnames -gt 0 ]; then
    echo ""
    echo "  超长类组合示例 (需要重构):"
    grep -r 'className="[^"]*"' src/ --include="*.tsx" -n 2>/dev/null | \
      awk -F'className="' '{
        split($2, arr, "\"");
        class_count = split(arr[1], classes, " ");
        if(class_count >= 8) {
          printf "    📍 %s (类数量: %d)\n", $1, class_count;
          printf "      → %s\n\n", substr(arr[1], 1, 80) "...";
        }
      }' | head -10
fi

# 特定复杂模式检测（增强版）
echo ""
echo "特定复杂模式深度检测:"
echo "检测需要提取为语义化类的特定模式..."

# Tooltip模式检测
tooltip_pattern=$(grep -r "absolute.*left-1/2.*-translate-x-1/2" src/ --include="*.tsx" 2>/dev/null | wc -l)
tooltip_complex=$(grep -r "absolute.*translate.*opacity.*hover.*transition" src/ --include="*.tsx" 2>/dev/null | wc -l)

# 按钮模式检测  
button_pattern=$(grep -r "px-[0-9].*py-[0-9].*bg-.*hover:bg-.*text-.*rounded" src/ --include="*.tsx" 2>/dev/null | wc -l)
button_states=$(grep -r "hover:.*focus:.*active:" src/ --include="*.tsx" 2>/dev/null | wc -l)

# 模态框模式检测
modal_pattern=$(grep -r "fixed.*inset.*z-[0-9].*flex.*items-center.*justify-center" src/ --include="*.tsx" 2>/dev/null | wc -l)
overlay_pattern=$(grep -r "fixed inset-0.*bg-black.*bg-opacity" src/ --include="*.tsx" 2>/dev/null | wc -l)

# 布局模式检测
grid_pattern=$(grep -r "grid grid-cols.*gap-[0-9]" src/ --include="*.tsx" 2>/dev/null | wc -l)
responsive_pattern=$(grep -r "sm:.*md:.*lg:" src/ --include="*.tsx" 2>/dev/null | wc -l)

echo "  📌 Tooltip 复杂定位模式: $tooltip_pattern 处"
echo "  📌 Tooltip 状态转换模式: $tooltip_complex 处"
echo "  📌 按钮多状态样式模式: $button_pattern 处"
echo "  📌 按钮交互状态模式: $button_states 处"
echo "  📌 模态框复杂布局模式: $modal_pattern 处"
echo "  📌 遮罩层模式: $overlay_pattern 处"
echo "  📌 网格布局模式: $grid_pattern 处"
echo "  📌 响应式设计模式: $responsive_pattern 处"

# 详细展示需要重构的复杂模式
if [ $tooltip_complex -gt 0 ] || [ $button_states -gt 0 ] || [ $modal_pattern -gt 0 ]; then
    echo ""
    echo "  🎯 需要重构的复杂模式示例:"
    
    if [ $tooltip_complex -gt 0 ]; then
        echo "    → Tooltip复杂模式:"
        grep -r "absolute.*translate.*opacity.*hover.*transition" src/ --include="*.tsx" -n 2>/dev/null | \
          head -2 | sed 's/^/      /'
        echo ""
    fi
    
    if [ $button_states -gt 0 ]; then
        echo "    → 按钮多状态模式:"  
        grep -r "hover:.*focus:.*active:" src/ --include="*.tsx" -n 2>/dev/null | \
          head -2 | sed 's/^/      /'
        echo ""
    fi
    
    if [ $modal_pattern -gt 0 ]; then
        echo "    → 模态框布局模式:"
        grep -r "fixed.*inset.*z-.*flex.*items-center.*justify-center" src/ --include="*.tsx" -n 2>/dev/null | \
          head -2 | sed 's/^/      /'
        echo ""
    fi
fi
echo ""

# 3. CSS文件架构分析
echo "3. CSS文件架构分析:"
echo "--------------------"

if [ -f "src/styles/index.css" ]; then
    main_css_lines=$(wc -l < src/styles/index.css)
    echo "主样式文件行数: $main_css_lines 行"
    
    if [ $main_css_lines -le 20 ]; then
        echo "  ✅ 主文件作为导入聚合器，架构良好"
    else
        echo "  ⚠️  主文件过大，建议进一步模块化"
    fi
else
    echo "❌ 未找到主样式文件 src/styles/index.css"
fi

# 检查CSS模块化情况
echo ""
echo "CSS模块化分析:"
css_files_count=$(find src/styles/ -name "*.css" 2>/dev/null | wc -l)
components_css_count=$(find src/styles/components/ -name "*.css" 2>/dev/null | wc -l)

echo "  CSS文件总数: $css_files_count"
echo "  组件级CSS文件: $components_css_count"

if [ $css_files_count -gt 5 ] && [ $components_css_count -gt 0 ]; then
    echo "  ✅ CSS架构已模块化"
else
    echo "  ⚠️  建议进一步模块化CSS架构"
fi

echo ""
echo "所有CSS文件详情:"
if [ -d "src/styles/" ]; then
    find src/styles/ -name "*.css" -exec bash -c 'echo "  $(basename {}) - $(wc -l < {}) 行"' \; 2>/dev/null | sort
else
    find src/ -name "*.css" -exec bash -c 'echo "  {} - $(wc -l < {}) 行"' \; 2>/dev/null | sort
fi
echo ""

# 4. 组件文件统计与分析
echo "4. 组件文件统计:"
echo "----------------"
tsx_files_count=$(find src/ -name "*.tsx" 2>/dev/null | wc -l)
ts_files_count=$(find src/ -name "*.ts" 2>/dev/null | wc -l)

echo "TypeScript React组件 (.tsx): $tsx_files_count 个"
echo "TypeScript模块 (.ts): $ts_files_count 个"

# 分析样式使用密度
echo ""
echo "样式使用密度分析:"
total_classnames=$(grep -r 'className=' src/ --include="*.tsx" 2>/dev/null | wc -l)
avg_classnames_per_file=$(echo "scale=1; $total_classnames / $tsx_files_count" | bc -l 2>/dev/null || echo "N/A")

echo "  总className使用次数: $total_classnames"
echo "  每个组件平均className数: $avg_classnames_per_file"

if [ $(echo "$avg_classnames_per_file > 10" | bc -l 2>/dev/null) ]; then
    echo "  ⚠️  样式使用密度较高，建议增加语义化类"
else
    echo "  ✅ 样式使用密度合理"
fi
echo ""

# 5. 语义化类检测
echo "5. 语义化类系统分析:"
echo "----------------------"

# 检测自定义语义化类的使用
semantic_classes=(
    "centered-container"
    "modal-overlay"
    "btn-base"
    "btn-primary"
    "btn-secondary"
    "input-base"
    "tooltip-content"
    "sidebar-nav"
    "chat-bubble"
)

echo "已定义的语义化类使用情况:"
total_semantic_usage=0

for class in "${semantic_classes[@]}"; do
    usage_count=$(grep -r "\\b$class\\b" src/ --include="*.tsx" 2>/dev/null | wc -l)
    total_semantic_usage=$((total_semantic_usage + usage_count))
    if [ $usage_count -gt 0 ]; then
        echo "  ✅ .$class: $usage_count 次使用"
    else
        echo "  ⚪ .$class: 未使用"
    fi
done

echo ""
echo "语义化类覆盖率:"
semantic_ratio=$(echo "scale=1; $total_semantic_usage * 100 / $total_classnames" | bc -l 2>/dev/null || echo "0")
echo "  语义化类使用占比: ${semantic_ratio}%"

if [ $(echo "$semantic_ratio > 15" | bc -l 2>/dev/null) ]; then
    echo "  ✅ 语义化类使用良好"
elif [ $(echo "$semantic_ratio > 5" | bc -l 2>/dev/null) ]; then
    echo "  � 语义化类使用中等，可继续提升"
else
    echo "  �🔴 语义化类使用不足，需要加强"
fi
echo ""

# 6. 文件清理检测
echo "6. 文件清理检测:"
echo "----------------"

# 检查是否存在旧的样式文件
old_files_found=0

if [ -f "src/index.css" ]; then
    old_index_lines=$(wc -l < src/index.css)
    echo "⚠️  发现旧样式文件: src/index.css ($old_index_lines 行)"
    echo "   建议删除，已被 src/styles/index.css 替代"
    old_files_found=1
fi

if [ -f "src/App.css" ]; then
    echo "⚠️  发现旧样式文件: src/App.css"
    echo "   建议检查是否可以删除或迁移"
    old_files_found=1
fi

# 检查未使用的CSS文件
unused_css=$(find src/ -name "*.css" -exec grep -L "@import\|\..*{" {} \; 2>/dev/null)
if [ ! -z "$unused_css" ]; then
    echo "⚠️  可能未使用的CSS文件:"
    echo "$unused_css" | sed 's/^/   /'
    old_files_found=1
fi

if [ $old_files_found -eq 0 ]; then
    echo "✅ 未发现需要清理的旧文件"
fi
echo ""

# 7. 质量评分和重构建议
echo "7. 样式质量评分和重构建议:"
echo "============================="

# 计算质量分数
score=100
reasons=()

# 内联样式扣分
if [ $inline_styles_count -gt 10 ]; then
    score=$((score - 30))
    reasons+=("内联样式过多($inline_styles_count处): -30分")
elif [ $inline_styles_count -gt 5 ]; then
    score=$((score - 15))
    reasons+=("内联样式较多($inline_styles_count处): -15分")
elif [ $inline_styles_count -gt 0 ]; then
    score=$((score - 5))
    reasons+=("存在少量内联样式($inline_styles_count处): -5分")
fi

# 复杂类组合扣分
if [ $complex_classnames -gt 10 ]; then
    score=$((score - 25))
    reasons+=("复杂类组合过多($complex_classnames处): -25分")
elif [ $complex_classnames -gt 5 ]; then
    score=$((score - 15))
    reasons+=("复杂类组合较多($complex_classnames处): -15分")
elif [ $complex_classnames -gt 0 ]; then
    score=$((score - 8))
    reasons+=("存在复杂类组合($complex_classnames处): -8分")
fi

# CSS架构扣分
if [ $css_files_count -lt 3 ]; then
    score=$((score - 20))
    reasons+=("CSS未模块化: -20分")
elif [ $main_css_lines -gt 100 ]; then
    score=$((score - 10))
    reasons+=("主CSS文件过大: -10分")
fi

# 语义化类加分/扣分
if [ $(echo "$semantic_ratio > 20" | bc -l 2>/dev/null) ]; then
    score=$((score + 10))
    reasons+=("语义化类使用优秀: +10分")
elif [ $(echo "$semantic_ratio < 5" | bc -l 2>/dev/null) ]; then
    score=$((score - 15))
    reasons+=("语义化类使用不足: -15分")
fi

# 文件清理扣分
if [ $old_files_found -gt 0 ]; then
    score=$((score - 10))
    reasons+=("存在需清理的旧文件: -10分")
fi

# 确保分数不低于0
if [ $score -lt 0 ]; then
    score=0
fi

echo "📊 样式质量评分: ${score}/100"
echo ""

# 输出评分详情
if [ ${#reasons[@]} -gt 0 ]; then
    echo "评分详情:"
    for reason in "${reasons[@]}"; do
        echo "  • $reason"
    done
    echo ""
fi

# 根据分数给出等级和建议
if [ $score -ge 90 ]; then
    echo "🏆 等级: 优秀 - 样式架构非常好！"
    echo "建议: 继续保持现有的良好实践"
elif [ $score -ge 75 ]; then
    echo "🥈 等级: 良好 - 样式架构基本合格"
    echo "建议: 继续完善语义化类系统，减少复杂类组合"
elif [ $score -ge 60 ]; then
    echo "🥉 等级: 中等 - 需要进一步优化"
    echo "建议: 优先处理内联样式和复杂类组合，加强CSS模块化"
elif [ $score -ge 40 ]; then
    echo "⚠️  等级: 待改进 - 存在较多问题"
    echo "建议: 按优先级依次处理：内联样式 → 类组合简化 → CSS架构重构"
else
    echo "🚨 等级: 需要重构 - 样式问题严重"
    echo "建议: 立即开始全面样式重构，建议参考 CSS_ARCHITECTURE_GUIDE.md"
fi

echo ""
echo "🎯 优先处理建议:"

# 优先级建议
priority_high=()
priority_medium=()
priority_low=()

if [ $inline_styles_count -gt 5 ]; then
    priority_high+=("消除内联样式 ($inline_styles_count 处)")
fi

if [ $complex_classnames -gt 8 ]; then
    priority_high+=("重构复杂类组合 ($complex_classnames 处)")
fi

if [ $old_files_found -gt 0 ]; then
    priority_medium+=("清理旧样式文件")
fi

if [ $css_files_count -lt 5 ]; then
    priority_medium+=("完善CSS模块化架构")
fi

if [ $(echo "$semantic_ratio < 10" | bc -l 2>/dev/null) ]; then
    priority_medium+=("扩展语义化类系统")
fi

if [ $tooltip_complex -gt 3 ] || [ $button_states -gt 5 ]; then
    priority_medium+=("提取常用组件模式为语义化类")
fi

if [ $responsive_pattern -gt 10 ]; then
    priority_low+=("优化响应式设计模式")
fi

# 输出优先级建议
if [ ${#priority_high[@]} -gt 0 ]; then
    echo ""
    echo "🔴 高优先级 (立即处理):"
    for item in "${priority_high[@]}"; do
        echo "  • $item"
    done
fi

if [ ${#priority_medium[@]} -gt 0 ]; then
    echo ""
    echo "🟡 中优先级 (近期处理):"
    for item in "${priority_medium[@]}"; do
        echo "  • $item"
    done
fi

if [ ${#priority_low[@]} -gt 0 ]; then
    echo ""
    echo "🟢 低优先级 (长期优化):"
    for item in "${priority_low[@]}"; do
        echo "  • $item"
    done
fi

echo ""
echo "=== 分析完成 ==="
echo "📚 详细重构指南请参考: CSS_ARCHITECTURE_GUIDE.md"
echo "📋 具体任务清单请参考: CSS_REFACTOR_TASK_LIST.md"
echo ""
echo "💡 使用 'npm run lint:css' 进行CSS语法检查"
echo "💡 使用 'npm run build' 验证样式构建是否正常"
