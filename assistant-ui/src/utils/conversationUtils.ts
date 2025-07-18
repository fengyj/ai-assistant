import type { Conversation } from '../types';

export const groupConversationsByTime = (conversations: Conversation[]) => {
  const now = new Date();
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  const yesterday = new Date(today.getTime() - 24 * 60 * 60 * 1000);
  const weekAgo = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000);
  const monthAgo = new Date(today.getTime() - 30 * 24 * 60 * 60 * 1000);

  const groups: { [key: string]: Conversation[] } = {
    '今天': [],
    '昨天': [],
    '7天内': [],
    '一个月内': [],
  };

  const monthlyGroups: { [key: string]: Conversation[] } = {};

  conversations.forEach(conv => {
    const convDate = new Date(conv.createdAt);
    const convDateOnly = new Date(convDate.getFullYear(), convDate.getMonth(), convDate.getDate());

    if (convDateOnly.getTime() === today.getTime()) {
      groups['今天'].push(conv);
    } else if (convDateOnly.getTime() === yesterday.getTime()) {
      groups['昨天'].push(conv);
    } else if (convDate >= weekAgo) {
      groups['7天内'].push(conv);
    } else if (convDate >= monthAgo) {
      groups['一个月内'].push(conv);
    } else {
      const monthKey = `${convDate.getFullYear()}年${String(convDate.getMonth() + 1).padStart(2, '0')}月`;
      if (!monthlyGroups[monthKey]) {
        monthlyGroups[monthKey] = [];
      }
      monthlyGroups[monthKey].push(conv);
    }
  });

  // 合并所有分组，过滤空组
  const result: { [key: string]: Conversation[] } = {};
  Object.entries(groups).forEach(([key, convs]) => {
    if (convs.length > 0) {
      result[key] = convs;
    }
  });

  // 添加月份分组，按时间倒序
  const sortedMonthKeys = Object.keys(monthlyGroups).sort((a, b) => b.localeCompare(a));
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
