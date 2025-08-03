import type { Conversation } from '../types';

export const groupConversationsByTime = (conversations: Conversation[]) => {
  const now = new Date();
  const groups: { [key: string]: Conversation[] } = {
    '今天': [],
    '昨天': [],
    '本周': [],
    '本月': [],
    '更早': []
  };

  conversations.forEach(conv => {
    const msgDate = new Date(conv.updatedAt);
    const diffInMs = now.getTime() - msgDate.getTime();
    const diffInDays = Math.floor(diffInMs / (1000 * 60 * 60 * 24));

    if (diffInDays === 0) {
      groups['今天'].push(conv);
    } else if (diffInDays === 1) {
      groups['昨天'].push(conv);
    } else if (diffInDays <= 7) {
      groups['本周'].push(conv);
    } else if (diffInDays <= 30) {
      groups['本月'].push(conv);
    } else {
      groups['更早'].push(conv);
    }
  });

  // 按月份分组老消息
  const monthlyGroups: { [key: string]: Conversation[] } = {};
  groups['更早'].forEach(conv => {
    const date = new Date(conv.updatedAt);
    const monthKey = `${date.getFullYear()}年${date.getMonth() + 1}月`;
    if (!monthlyGroups[monthKey]) {
      monthlyGroups[monthKey] = [];
    }
    monthlyGroups[monthKey].push(conv);
  });

  // 创建最终结果，排除空的分组
  const result: { [key: string]: Conversation[] } = {};
  
  ['今天', '昨天', '本周', '本月'].forEach(key => {
    if (groups[key].length > 0) {
      result[key] = groups[key];
    }
  });

  // 按时间倒序添加月份分组
  const sortedMonthKeys = Object.keys(monthlyGroups).sort((a, b) => {
    const dateA = new Date(a.replace('年', '-').replace('月', '-01'));
    const dateB = new Date(b.replace('年', '-').replace('月', '-01'));
    return dateB.getTime() - dateA.getTime();
  });
  
  sortedMonthKeys.forEach(key => {
    result[key] = monthlyGroups[key];
  });

  return result;
};

export const generateAIResponse = (userMessage: string, files: File[] = [], getFileIcon?: (file: File) => string): string => {
  // 如果有文件，生成特定的文件响应
  if (files.length > 0) {
    // 提供默认的getFileIcon函数，如果没有传入的话
    const defaultGetFileIcon = (file: File) => {
      if (file.type.startsWith('image/')) return '🖼️';
      if (file.type.includes('pdf')) return '📄';
      if (file.type.includes('word') || file.type.includes('document')) return '📝';
      if (file.type.includes('excel') || file.type.includes('spreadsheet')) return '📊';
      if (file.type.includes('text')) return '📄';
      return '📎';
    };

    const iconFunction = getFileIcon || defaultGetFileIcon;
    const fileInfo = files.map(file => {
      const isImage = file.type.startsWith('image/');
      const icon = iconFunction(file);
      return `${icon} **${file.name}** (${(file.size / 1024).toFixed(1)}KB${isImage ? ' - 图片文件' : ''})`;
    }).join('\n');
    
    return `我已收到您上传的 **${files.length}个文件**：

${fileInfo}

${userMessage ? `您的消息："${userMessage}"` : ''}

## 文件处理能力

我可以帮助您：
- 📷 **图片文件**：分析图片内容、识别文字、解答图片相关问题
- 📄 **文档文件**：解读PDF、Word文档内容
- 📊 **数据文件**：分析Excel、CSV数据
- 💾 **代码文件**：审查代码、提供优化建议

请告诉我您希望对这些文件进行什么操作？`;
  }
  
  const responses = [
    `I understand you said: "${userMessage}". Here's my response with **markdown** support!

You can test various formatting like *italic text*, **bold text**, and \`inline code\`.`,

    `Thank you for your message about "${userMessage}". I can help you with:

## Markdown Features

### Supported Elements
- **Bold text** with double asterisks
- *Italic text* with single asterisks  
- \`Inline code\` with backticks
- Links: [GitHub](https://github.com)

### Code Examples
Here's a JavaScript example:

\`\`\`javascript
const [count, setCount] = useState(0);

useEffect(() => {
  console.log("Count updated:", count);
}, [count]);
\`\`\`

How can I assist you further?`,

    `About "${userMessage}" - here's a comprehensive overview with a data table:

## Feature Comparison

| Feature | Basic Plan | Pro Plan | Enterprise |
|---------|------------|----------|------------|
| **Users** | 1-5 | 6-50 | Unlimited |
| **Storage** | 10GB | 100GB | 1TB+ |
| **Support** | Email | Priority | 24/7 Phone |
| **Price** | $9/month | $29/month | Custom |

### Additional Features
- ✅ All plans include **basic features**
- ✅ Pro and Enterprise get *advanced analytics*
- ✅ Enterprise includes \`custom integrations\`

Want to know more about any specific plan?`
  ];
  
  return responses[Math.floor(Math.random() * responses.length)];
};

export const formatRelativeTime = (date: Date): string => {
  const now = new Date();
  const diffInMs = now.getTime() - date.getTime();
  const diffInMinutes = Math.floor(diffInMs / (1000 * 60));
  const diffInHours = Math.floor(diffInMs / (1000 * 60 * 60));
  const diffInDays = Math.floor(diffInMs / (1000 * 60 * 60 * 24));

  if (diffInMinutes < 1) return '刚刚';
  if (diffInMinutes < 60) return `${diffInMinutes}分钟前`;
  if (diffInHours < 24) return `${diffInHours}小时前`;
  if (diffInDays < 7) return `${diffInDays}天前`;
  
  return date.toLocaleDateString('zh-CN', { 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric' 
  });
};
