import { useState, useEffect, useRef } from 'react';
import mermaid from 'mermaid';

interface Message {
  id: string;
  content: string;
  isUser: boolean;
  timestamp: Date;
}

interface Conversation {
  id: string;
  title: string;
  messages: Message[];
  createdAt: Date;
}

export default function App() {
  // 创建对textarea的引用
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  
  // 主题状态
  const [isDarkMode, setIsDarkMode] = useState(false);
  // 跟踪消息是否刚刚发送，用于自动聚焦
  const [messageJustSent, setMessageJustSent] = useState(false);
  
  // 初始化Mermaid
  useEffect(() => {
    mermaid.initialize({
      startOnLoad: false,
      theme: isDarkMode ? 'dark' : 'default',
      securityLevel: 'loose',
      fontFamily: 'inherit'
    });
  }, [isDarkMode]);
  
  // 侧边栏状态
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  
  // 对话状态
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [currentConversationId, setCurrentConversationId] = useState<string | null>(null);
  
  // 消息输入状态
  const [message, setMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  
  // 消息发送后自动聚焦输入框
  useEffect(() => {
    if (messageJustSent && textareaRef.current && !isLoading) {
      // 延迟一下再聚焦，确保DOM已更新
      const focusTimer = setTimeout(() => {
        textareaRef.current?.focus();
        setMessageJustSent(false);
      }, 100);
      return () => clearTimeout(focusTimer);
    }
  }, [messageJustSent, isLoading]);
  
  // 文件上传状态
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [isDragOver, setIsDragOver] = useState(false);
  
  // 用户状态
  const [user, setUser] = useState<{id: string, name: string, avatar?: string} | null>(null);
  const [showLoginDialog, setShowLoginDialog] = useState(false);
  const [showSettingsDialog, setShowSettingsDialog] = useState(false);
  
  // 自动调整textarea高度
  const adjustTextareaHeight = (element: HTMLTextAreaElement) => {
    element.style.height = 'auto';
    element.style.height = Math.min(element.scrollHeight, 200) + 'px';
  };
  
  // 处理消息输入变化
  const handleMessageChange = (e: any) => {
    setMessage(e.target.value);
    adjustTextareaHeight(e.target);
  };
  
  // 模型选择
  const [selectedModel, setSelectedModel] = useState('gpt-4');
  
  // 文件处理函数
  const handleFileSelect = (files: File[]) => {
    const validFiles = files.filter(file => {
      // 限制文件大小为10MB
      if (file.size > 10 * 1024 * 1024) {
        alert(`文件 ${file.name} 超过10MB限制`);
        return false;
      }
      return true;
    });
    setSelectedFiles(prev => [...prev, ...validFiles]);
  };
  
  const removeFile = (index: number) => {
    setSelectedFiles(prev => prev.filter((_, i) => i !== index));
  };
  
  const handleDragOver = (e: any) => {
    e.preventDefault();
    setIsDragOver(true);
  };
  
  const handleDragLeave = (e: any) => {
    e.preventDefault();
    setIsDragOver(false);
  };
  
  const handleDrop = (e: any) => {
    e.preventDefault();
    setIsDragOver(false);
    const files = Array.from(e.dataTransfer.files) as File[];
    handleFileSelect(files);
  };
  
  // 添加Toast通知状态
  const [toastMessage, setToastMessage] = useState<string | null>(null);
  
  // 显示Toast通知
  const showToast = (message: string) => {
    setToastMessage(message);
    setTimeout(() => setToastMessage(null), 3000);
  };
  
  // 处理粘贴事件（Ctrl+V）
  const handlePaste = (e: ClipboardEvent) => {
    const items = e.clipboardData?.items;
    if (!items) return;
    
    const files: File[] = [];
    
    for (let i = 0; i < items.length; i++) {
      const item = items[i];
      
      // 只处理文件类型的item
      if (item.kind === 'file') {
        const file = item.getAsFile();
        if (file) {
          // 如果是图片类型，重命名为screenshot格式
          if (file.type.startsWith('image/')) {
            const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
            const fileExtension = file.type.split('/')[1] || 'png';
            const renamedFile = new File([file], `screenshot-${timestamp}.${fileExtension}`, {
              type: file.type
            });
            files.push(renamedFile);
          } else {
            // 非图片文件保持原名
            files.push(file);
          }
        }
      }
    }
    
    if (files.length > 0) {
      e.preventDefault(); // 阻止默认粘贴行为
      handleFileSelect(files);
      
      // 显示粘贴成功提示
      const fileTypes = files.map(f => f.type.startsWith('image/') ? '截图' : '文件').join('、');
      const message = `✅ 已粘贴 ${files.length} 个${fileTypes}`;
      showToast(message);
      
      // 粘贴后自动聚焦到输入框
      setTimeout(() => {
        const textarea = document.querySelector('textarea');
        if (textarea) {
          textarea.focus();
        }
      }, 100);
    }
  };
  
  // 添加全局粘贴事件监听
  useEffect(() => {
    const handleGlobalPaste = (e: ClipboardEvent) => {
      // 只在聊天界面活跃且输入框聚焦时处理粘贴
      const activeElement = document.activeElement;
      const isInputFocused = activeElement?.tagName === 'TEXTAREA' && activeElement?.id !== 'file-upload';
      
      if (isInputFocused) {
        handlePaste(e);
      }
    };
    
    document.addEventListener('paste', handleGlobalPaste);
    
    return () => {
      document.removeEventListener('paste', handleGlobalPaste);
    };
  }, []);
  
  const getFileIcon = (file: File) => {
    if (file.type.startsWith('image/')) return '🖼️';
    if (file.type.includes('pdf')) return '📄';
    if (file.type.includes('word') || file.type.includes('document')) return '📝';
    if (file.type.includes('excel') || file.type.includes('spreadsheet')) return '📊';
    if (file.type.includes('text')) return '📄';
    return '📎';
  };
  
  // 按时间分组对话
  const groupConversationsByTime = (conversations: Conversation[]) => {
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

    // 按月份分组的对象
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

  // 获取分组后的对话
  const groupedConversations = groupConversationsByTime(conversations);
  
  // 获取当前对话
  const currentConversation = conversations.find(c => c.id === currentConversationId);
  
  // Mermaid渲染函数
  const renderMermaidChart = (code: string, id: string) => {
    // 直接返回包含mermaid代码的div，让后续的useEffect处理
    return `<div class="mermaid-container my-4 p-4 border rounded-lg bg-white dark:bg-gray-800" data-mermaid-code="${encodeURIComponent(code)}" data-mermaid-id="${id}">
      <div class="text-gray-500 text-sm text-center">正在渲染Mermaid图表...</div>
    </div>`;
  };
  
  // 简单的Markdown渲染函数
  const renderMarkdown = (text: string, isUserMessage = false) => {
    const codeClass = isUserMessage 
      ? 'bg-blue-600/50 px-1 py-0.5 rounded-sm text-sm font-mono'
      : 'bg-gray-100 dark:bg-gray-800 px-1 py-0.5 rounded-sm text-sm font-mono';
      
    const preClass = isUserMessage 
      ? 'bg-blue-600/50 p-3 rounded-lg mt-3 mb-3 overflow-x-auto'
      : 'bg-gray-100 dark:bg-gray-800 p-3 rounded-lg mt-3 mb-3 overflow-x-auto';
      
    const linkClass = isUserMessage 
      ? 'text-blue-200 hover:text-blue-100 underline'
      : 'text-blue-500 hover:text-blue-600 underline';

    const tableClass = isUserMessage
      ? 'min-w-full border-collapse border border-blue-300/50 mt-3 mb-3'
      : 'min-w-full border-collapse border border-gray-300 dark:border-gray-600 mt-3 mb-3';
      
    const thClass = isUserMessage
      ? 'border border-blue-300/50 px-3 py-2 bg-blue-600/30 font-semibold text-left'
      : 'border border-gray-300 dark:border-gray-600 px-3 py-2 bg-gray-100 dark:bg-gray-700 font-semibold text-left';
      
    const tdClass = isUserMessage
      ? 'border border-blue-300/50 px-3 py-2'
      : 'border border-gray-300 dark:border-gray-600 px-3 py-2';
    
    let result = text
      // 表格处理（优先处理）
      .replace(/\|(.+)\|\n\|[-:\s|]+\|\n((?:\|.+\|\n?)*)/g, (_, header, rows) => {
        const headerCells = header.split('|').map((cell: string) => cell.trim()).filter((cell: string) => cell);
        const headerRow = headerCells.map((cell: string) => `<th class="${thClass}">${cell}</th>`).join('');
        
        const bodyRows = rows.trim().split('\n').map((row: string) => {
          const cells = row.split('|').map((cell: string) => cell.trim()).filter((cell: string) => cell);
          return `<tr>${cells.map((cell: string) => `<td class="${tdClass}">${cell}</td>`).join('')}</tr>`;
        }).join('');
        
        return `<div class="overflow-x-auto"><table class="${tableClass}"><thead><tr>${headerRow}</tr></thead><tbody>${bodyRows}</tbody></table></div>`;
      })
      // Mermaid图表处理（在代码块之前处理）
      .replace(/```mermaid\n([\s\S]*?)```/g, (_, code) => {
        const chartId = Math.random().toString(36).substr(2, 9);
        return renderMermaidChart(code.trim(), chartId);
      })
      // 代码块处理（优先处理，避免其内容被其他规则影响）
      .replace(/```(\w+)?\n([\s\S]*?)```/g, `<pre class="${preClass}"><code class="text-sm font-mono">$2</code></pre>`)
      .replace(/```([\s\S]*?)```/g, `<pre class="${preClass}"><code class="text-sm font-mono">$1</code></pre>`)
      // 标题
      .replace(/^### (.*$)/gm, '<h3 class="text-lg font-semibold mt-4 mb-2">$1</h3>')
      .replace(/^## (.*$)/gm, '<h2 class="text-xl font-semibold mt-4 mb-2">$1</h2>')
      .replace(/^# (.*$)/gm, '<h1 class="text-2xl font-bold mt-4 mb-2">$1</h1>')
      // 列表 - 使用更紧凑的样式
      .replace(/^- (.*$)/gm, '<li class="ml-4 list-disc leading-snug">$1</li>')
      .replace(/^\d+\. (.*$)/gm, '<li class="ml-4 list-decimal leading-snug">$1</li>')
      // 粗体和斜体
      .replace(/\*\*(.*?)\*\*/g, '<strong class="font-semibold">$1</strong>')
      .replace(/\*(.*?)\*/g, '<em class="italic">$1</em>')
      // 行内代码
      .replace(/`([^`]+)`/g, `<code class="${codeClass}">$1</code>`)
      // 链接
      .replace(/\[([^\]]+)\]\(([^)]+)\)/g, `<a href="$2" class="${linkClass}" target="_blank" rel="noopener noreferrer">$1</a>`);
    
    // 处理段落和换行
    // 将连续的空行替换为段落分隔符
    result = result
      .split(/\n\s*\n/)  // 按照空行分割成段落
      .map(paragraph => paragraph.trim())  // 去除每段首尾空白
      .filter(paragraph => paragraph.length > 0)  // 过滤空段落
      .map(paragraph => {
        // 对于包含HTML标签的段落（如标题、列表、表格等），不包装在p标签中
        if (paragraph.match(/^<(h[1-6]|li|pre|div)/)) {
          return paragraph;
        }
        // 普通段落包装在p标签中，单个换行转为br
        return `<p class="mb-3">${paragraph.replace(/\n/g, '<br />')}</p>`;
      })
      .join('');
    
    // 移除列表项之间的多余换行和br标签
    result = result
      .replace(/(<\/li>)\s*<br\s*\/?>\s*(<li)/g, '$1$2')
      .replace(/(<\/li>)\s*(<li)/g, '$1$2');
    
    return result;
  };
  
  // 初始化默认对话
  useEffect(() => {
    if (conversations.length === 0) {
      const now = new Date();
      const defaultConversations: Conversation[] = [
        {
          id: '1',
          title: 'New Chat',
          messages: [{
            id: '1',
            content: 'Hello! I\'m your AI assistant. How can I help you today?',
            isUser: false,
            timestamp: new Date()
          }],
          createdAt: new Date()
        },
        {
          id: '2',
          title: '如何学习React',
          messages: [{
            id: '2',
            content: '请问如何快速学习React？',
            isUser: true,
            timestamp: new Date(now.getTime() - 2 * 60 * 60 * 1000)
          }],
          createdAt: new Date(now.getTime() - 2 * 60 * 60 * 1000)
        },
        {
          id: '3',
          title: 'TypeScript基础',
          messages: [{
            id: '3',
            content: 'TypeScript的基本语法是什么？',
            isUser: true,
            timestamp: new Date(now.getTime() - 25 * 60 * 60 * 1000)
          }],
          createdAt: new Date(now.getTime() - 25 * 60 * 60 * 1000)
        },
        {
          id: '4',
          title: '数据库设计',
          messages: [{
            id: '4',
            content: '如何设计一个好的数据库？',
            isUser: true,
            timestamp: new Date(now.getTime() - 3 * 24 * 60 * 60 * 1000)
          }],
          createdAt: new Date(now.getTime() - 3 * 24 * 60 * 60 * 1000)
        },
        {
          id: '5',
          title: 'Python爬虫教程',
          messages: [{
            id: '5',
            content: 'Python爬虫的基础知识',
            isUser: true,
            timestamp: new Date(now.getTime() - 15 * 24 * 60 * 60 * 1000)
          }],
          createdAt: new Date(now.getTime() - 15 * 24 * 60 * 60 * 1000)
        },
        {
          id: '6',
          title: '算法学习',
          messages: [{
            id: '6',
            content: '常见的排序算法有哪些？',
            isUser: true,
            timestamp: new Date(now.getTime() - 45 * 24 * 60 * 60 * 1000)
          }],
          createdAt: new Date(now.getTime() - 45 * 24 * 60 * 60 * 1000)
        },
        {
          id: '7',
          title: 'Web开发入门',
          messages: [{
            id: '7',
            content: 'Web开发需要学习哪些技术？',
            isUser: true,
            timestamp: new Date(now.getTime() - 120 * 24 * 60 * 60 * 1000)
          }],
          createdAt: new Date(now.getTime() - 120 * 24 * 60 * 60 * 1000)
        }
      ];
      setConversations(defaultConversations);
      setCurrentConversationId('1');
    }
  }, [conversations.length]);
  
  // 处理Mermaid图表渲染
  useEffect(() => {
    const renderMermaidCharts = async () => {
      const mermaidContainers = document.querySelectorAll('.mermaid-container[data-mermaid-code]:not([data-processed])');
      
      for (const container of mermaidContainers) {
        try {
          const code = decodeURIComponent(container.getAttribute('data-mermaid-code') || '');
          const id = container.getAttribute('data-mermaid-id') || '';
          
          if (code) {
            container.setAttribute('data-processed', 'true');
            const { svg } = await mermaid.render(`mermaid-svg-${id}-${Date.now()}`, code);
            container.innerHTML = svg;
          }
        } catch (error) {
          container.innerHTML = `<div class="text-red-600 text-sm p-3 border border-red-200 rounded-sm">Mermaid渲染错误: ${(error as Error).message}</div>`;
        }
      }
    };
    
    // 延迟执行以确保DOM已更新
    const timer = setTimeout(renderMermaidCharts, 100);
    return () => clearTimeout(timer);
  });
  
  // 主题切换
  const toggleTheme = () => {
    setIsDarkMode(!isDarkMode);
  };
  
  // 创建新对话
  const createNewConversation = () => {
    const newConversation: Conversation = {
      id: Date.now().toString(),
      title: 'New Chat',
      messages: [{
        id: Date.now().toString(),
        content: 'Hello! I\'m your AI assistant. How can I help you today?',
        isUser: false,
        timestamp: new Date()
      }],
      createdAt: new Date()
    };
    setConversations(prev => [newConversation, ...prev]);
    setCurrentConversationId(newConversation.id);
  };
  
  // 删除对话
  const deleteConversation = (id: string) => {
    setConversations(prev => prev.filter(c => c.id !== id));
    if (currentConversationId === id) {
      const remaining = conversations.filter(c => c.id !== id);
      setCurrentConversationId(remaining.length > 0 ? remaining[0].id : null);
    }
  };
  
  // 发送消息
  const sendMessage = () => {
    if ((!message.trim() && selectedFiles.length === 0) || !currentConversationId) return;
    
    // 构建消息内容
    let messageContent = message;
    if (selectedFiles.length > 0) {
      const fileList = selectedFiles.map(file => 
        `📎 ${file.name} (${(file.size / 1024).toFixed(1)}KB)`
      ).join('\n');
      messageContent = message ? `${message}\n\n**附件：**\n${fileList}` : `**附件：**\n${fileList}`;
    }
    
    const userMessage: Message = {
      id: Date.now().toString(),
      content: messageContent,
      isUser: true,
      timestamp: new Date()
    };
    
    // 更新对话消息
    setConversations(prev => prev.map(conv => 
      conv.id === currentConversationId 
        ? { ...conv, messages: [...conv.messages, userMessage] }
        : conv
    ));
    
    // 更新对话标题（如果是第一条用户消息）
    if (currentConversation?.messages.filter(m => m.isUser).length === 0) {
      const titleText = message || (selectedFiles.length > 0 ? `${selectedFiles.length}个文件` : 'New Chat');
      setConversations(prev => prev.map(conv => 
        conv.id === currentConversationId 
          ? { ...conv, title: titleText.length > 30 ? titleText.substring(0, 30) + '...' : titleText }
          : conv
      ));
    }
    
    const currentMessage = message;
    const currentFiles = selectedFiles;
    setMessage('');
    setSelectedFiles([]); // 清空已选文件
    setIsLoading(true);
    setMessageJustSent(true); // 标记消息刚刚发送
    
    // 重置textarea高度
    setTimeout(() => {
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
    }, 0);
    
    // 模拟AI回复
    const timeoutId = setTimeout(() => {
      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: generateAIResponse(currentMessage, currentFiles),
        isUser: false,
        timestamp: new Date()
      };
      
      setConversations(prev => prev.map(conv => 
        conv.id === currentConversationId 
          ? { ...conv, messages: [...conv.messages, aiMessage] }
          : conv
      ));
      setIsLoading(false);
      setMessageJustSent(true); // 回复完成后标记，触发聚焦
    }, 1000);
    
    // 保存超时ID以便可以取消
    (window as any).currentRequestTimeout = timeoutId;
  };
  
  // 取消请求
  const cancelRequest = () => {
    if ((window as any).currentRequestTimeout) {
      clearTimeout((window as any).currentRequestTimeout);
      (window as any).currentRequestTimeout = null;
    }
    setIsLoading(false);
    setMessageJustSent(true); // 标记消息刚刚处理完成
    
    // 显示取消消息
    showToast('已取消生成');
  };
  
  // 处理用户状态栏点击
  const handleUserStatusClick = () => {
    if (user) {
      setShowSettingsDialog(true);
    } else {
      setShowLoginDialog(true);
    }
  };
  
  // 处理登录
  const handleLogin = (username: string, password: string) => {
    // 模拟登录逻辑
    if (username && password) {
      setUser({
        id: '1',
        name: username,
        avatar: `https://api.dicebear.com/7.x/avatars/svg?seed=${username}`
      });
      setShowLoginDialog(false);
      showToast('登录成功');
    }
  };
  
  // 处理退出登录
  const handleLogout = () => {
    setUser(null);
    setShowSettingsDialog(false);
    showToast('已退出登录');
  };
  
  // 生成AI回复（模拟）
  const generateAIResponse = (userMessage: string, files: File[] = []) => {
    // 如果有文件，生成特定的文件响应
    if (files.length > 0) {
      const fileInfo = files.map(file => {
        const isImage = file.type.startsWith('image/');
        const icon = getFileIcon(file);
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

### Lists
1. Numbered lists work
2. Multiple items supported
3. Easy to read format

How can I assist you further?`,

      `Regarding "${userMessage}", I'd be happy to help! 

# Key Points

## Understanding
I can process various types of questions and provide **detailed responses**.

## Formatting Support
- **Bold formatting** for emphasis
- *Italic formatting* for style
- \`Code snippets\` for technical content
- Proper line breaks and spacing

## Code Handling
\`\`\`python
def hello_world():
    print("Hello, World!")
    return "Success"
\`\`\`

### What would you like to explore next?

Feel free to test any Markdown formatting - I support headings, lists, code blocks, links, and more!`,

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

Want to know more about any specific plan?`,

      `Great question about "${userMessage}"! Let me show you with a flow diagram:

## Process Flow

\`\`\`mermaid
graph TD
    A[用户输入] --> B{验证输入}
    B -->|有效| C[处理请求]
    B -->|无效| D[显示错误]
    C --> E[生成响应]
    E --> F[返回结果]
    D --> G[重新输入]
    G --> A
    F --> H[结束]
\`\`\`

### Sequence Diagram

\`\`\`mermaid
sequenceDiagram
    participant U as 用户
    participant S as 系统
    participant D as 数据库
    
    U->>S: 发送请求
    S->>D: 查询数据
    D-->>S: 返回数据
    S-->>U: 响应结果
\`\`\`

These diagrams help visualize the process flow!`
    ];
    
    return responses[Math.floor(Math.random() * responses.length)];
  };
  
  return (
    <div className={`min-h-screen ${isDarkMode ? 'dark bg-gray-900' : 'bg-gray-50'} transition-colors`}>
      {/* Toast 通知 */}
      {toastMessage && (
        <div className="fixed top-4 right-4 z-50 animate-fade-in">
          <div className={`px-4 py-3 rounded-lg shadow-lg ${
            isDarkMode 
              ? 'bg-gray-800 text-white border border-gray-700' 
              : 'bg-white text-gray-800 border border-gray-200'
          }`}>
            <div className="flex items-center space-x-2">
              <span className="text-sm font-medium">{toastMessage}</span>
            </div>
          </div>
        </div>
      )}
      
      {/* 登录对话框 */}
      {showLoginDialog && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className={`${isDarkMode ? 'bg-gray-800' : 'bg-white'} rounded-lg p-6 w-96 max-w-sm mx-4`}>
            <h2 className={`text-xl font-semibold mb-4 ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>
              登录
            </h2>
            <form onSubmit={(e) => {
              e.preventDefault();
              const formData = new FormData(e.target as HTMLFormElement);
              handleLogin(
                formData.get('username') as string,
                formData.get('password') as string
              );
            }}>
              <div className="space-y-4">
                <div>
                  <label className={`block text-sm font-medium mb-1 ${isDarkMode ? 'text-gray-300' : 'text-gray-700'}`}>
                    用户名
                  </label>
                  <input
                    type="text"
                    name="username"
                    required
                    className={`w-full px-3 py-2 border rounded-md ${
                      isDarkMode 
                        ? 'bg-gray-700 border-gray-600 text-white placeholder-gray-400' 
                        : 'bg-white border-gray-300 text-gray-900 placeholder-gray-500'
                    } focus:ring-2 focus:ring-blue-500 focus:border-transparent`}
                    placeholder="请输入用户名"
                  />
                </div>
                <div>
                  <label className={`block text-sm font-medium mb-1 ${isDarkMode ? 'text-gray-300' : 'text-gray-700'}`}>
                    密码
                  </label>
                  <input
                    type="password"
                    name="password"
                    required
                    className={`w-full px-3 py-2 border rounded-md ${
                      isDarkMode 
                        ? 'bg-gray-700 border-gray-600 text-white placeholder-gray-400' 
                        : 'bg-white border-gray-300 text-gray-900 placeholder-gray-500'
                    } focus:ring-2 focus:ring-blue-500 focus:border-transparent`}
                    placeholder="请输入密码"
                  />
                </div>
              </div>
              <div className="flex justify-end space-x-3 mt-6">
                <button
                  type="button"
                  onClick={() => setShowLoginDialog(false)}
                  className={`px-4 py-2 rounded-md ${
                    isDarkMode 
                      ? 'text-gray-300 hover:bg-gray-700' 
                      : 'text-gray-700 hover:bg-gray-100'
                  } transition-colors`}
                >
                  取消
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
                >
                  登录
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
      
      {/* 设置对话框 */}
      {showSettingsDialog && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className={`${isDarkMode ? 'bg-gray-800' : 'bg-white'} rounded-lg p-6 w-96 max-w-sm mx-4`}>
            <h2 className={`text-xl font-semibold mb-4 ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>
              系统设置
            </h2>
            
            {/* 用户信息 */}
            {user && (
              <div className="mb-6">
                <div className="flex items-center space-x-3 mb-4">
                  <div className="w-12 h-12 rounded-full overflow-hidden bg-gray-300">
                    {user.avatar ? (
                      <img src={user.avatar} alt={user.name} className="w-full h-full object-cover" />
                    ) : (
                      <div className={`w-full h-full flex items-center justify-center text-lg font-medium ${
                        isDarkMode ? 'bg-gray-600 text-white' : 'bg-gray-300 text-gray-700'
                      }`}>
                        {user.name.charAt(0).toUpperCase()}
                      </div>
                    )}
                  </div>
                  <div>
                    <p className={`font-medium ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>
                      {user.name}
                    </p>
                    <p className={`text-sm ${isDarkMode ? 'text-gray-400' : 'text-gray-500'}`}>
                      ID: {user.id}
                    </p>
                  </div>
                </div>
              </div>
            )}
            
            {/* 设置选项 */}
            <div className="space-y-3 mb-6">
              <div className={`flex items-center justify-between p-3 rounded-md ${
                isDarkMode ? 'bg-gray-700' : 'bg-gray-50'
              }`}>
                <span className={`text-sm ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>
                  深色模式
                </span>
                <button
                  onClick={toggleTheme}
                  className={`w-12 h-6 rounded-full p-1 ${
                    isDarkMode ? 'bg-blue-600' : 'bg-gray-300'
                  } transition-colors`}
                >
                  <div className={`w-4 h-4 rounded-full bg-white transform transition-transform ${
                    isDarkMode ? 'translate-x-6' : 'translate-x-0'
                  }`}></div>
                </button>
              </div>
              
              <button className={`w-full text-left p-3 rounded-md transition-colors ${
                isDarkMode ? 'hover:bg-gray-700 text-white' : 'hover:bg-gray-50 text-gray-900'
              }`}>
                <span className="text-sm">数据导出</span>
              </button>
              
              <button className={`w-full text-left p-3 rounded-md transition-colors ${
                isDarkMode ? 'hover:bg-gray-700 text-white' : 'hover:bg-gray-50 text-gray-900'
              }`}>
                <span className="text-sm">清除缓存</span>
              </button>
            </div>
            
            <div className="flex justify-between">
              <button
                onClick={handleLogout}
                className="px-4 py-2 text-red-600 hover:bg-red-50 rounded-md transition-colors"
              >
                退出登录
              </button>
              <button
                onClick={() => setShowSettingsDialog(false)}
                className={`px-4 py-2 rounded-md ${
                  isDarkMode 
                    ? 'text-gray-300 hover:bg-gray-700' 
                    : 'text-gray-700 hover:bg-gray-100'
                } transition-colors`}
              >
                关闭
              </button>
            </div>
          </div>
        </div>
      )}
      
      <div className="flex h-screen">
        {/* 侧边栏 */}
        <div className={`${isSidebarOpen ? 'w-80' : 'w-0'} transition-all duration-300 overflow-hidden ${isDarkMode ? 'bg-gray-800' : 'bg-white'} border-r ${isDarkMode ? 'border-gray-700' : 'border-gray-200'} flex flex-col`}>
          <div className="p-4 flex flex-col flex-1 min-h-0">
            <div className="flex items-center justify-between mb-4 shrink-0">
              <h2 className={`text-xl font-bold ${isDarkMode ? 'text-white' : 'text-gray-800'}`}>
                AI Assistant
              </h2>
            </div>
            
            <div className="mt-4 flex flex-col flex-1 min-h-0">
              <h3 className={`text-sm font-medium ${isDarkMode ? 'text-gray-400' : 'text-gray-600'} mb-3`}>
                对话历史
              </h3>
              <div className="space-y-4 flex-1 overflow-y-auto overflow-x-hidden custom-scrollbar">
                {Object.keys(groupedConversations).length === 0 ? (
                  <div className={`text-center py-8 ${isDarkMode ? 'text-gray-500' : 'text-gray-400'}`}>
                    <div className="mb-2 opacity-50">💬</div>
                    <p className="text-sm">暂无对话历史</p>
                  </div>
                ) : (
                  Object.entries(groupedConversations).map(([groupName, groupConversations]) => (
                    <div key={groupName}>
                      <h4 className={`text-xs font-semibold ${isDarkMode ? 'text-gray-400' : 'text-gray-600'} mb-2 px-1 uppercase tracking-wide`}>
                        {groupName}
                      </h4>
                      <div className="space-y-1">
                        {groupConversations.map(conv => (
                          <div
                            key={conv.id}
                            className={`group px-3 py-2 rounded-md cursor-pointer transition-all duration-200 ${
                              currentConversationId === conv.id
                                ? (isDarkMode ? 'bg-blue-900/40 border-blue-400/60 shadow-lg' : 'bg-blue-50 border-blue-200 shadow-md')
                                : (isDarkMode ? 'hover:bg-gray-700 border-transparent hover:border-gray-600 hover:shadow-md' : 'hover:bg-gray-50 border-transparent hover:border-gray-300 hover:shadow-xs')
                            } border`}
                            onClick={() => setCurrentConversationId(conv.id)}
                          >
                            <div className="flex items-center justify-between">
                              <div className="flex-1 min-w-0">
                                <p className={`text-sm font-medium ${isDarkMode ? 'text-white' : 'text-gray-800'} truncate leading-tight`}>
                                  {conv.title}
                                </p>
                                <p className={`text-xs ${isDarkMode ? 'text-gray-400' : 'text-gray-500'} mt-1 leading-tight`}>
                                  {conv.createdAt.toLocaleDateString('zh-CN', { 
                                    month: 'short', 
                                    day: 'numeric',
                                    hour: '2-digit',
                                    minute: '2-digit'
                                  })}
                                </p>
                              </div>
                              <button
                                onClick={(e: any) => {
                                  e.stopPropagation();
                                  deleteConversation(conv.id);
                                }}
                                className={`p-1.5 rounded-sm opacity-0 group-hover:opacity-100 transition-opacity duration-200 ${isDarkMode ? 'hover:bg-gray-600 text-gray-400 hover:text-red-400' : 'hover:bg-gray-200 text-gray-500 hover:text-red-500'} shrink-0`}
                                title="删除对话"
                              >
                                <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                                  <path fillRule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clipRule="evenodd" />
                                </svg>
                              </button>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
            
            {/* 用户状态栏 */}
            <div 
              className={`mt-auto border-t ${isDarkMode ? 'border-gray-700' : 'border-gray-200'} p-3 cursor-pointer transition-colors ${
                isDarkMode ? 'hover:bg-gray-700' : 'hover:bg-gray-50'
              }`}
              onClick={handleUserStatusClick}
            >
              <div className="flex items-center space-x-3">
                {user ? (
                  <>
                    <div className="w-8 h-8 rounded-full overflow-hidden bg-gray-300">
                      {user.avatar ? (
                        <img src={user.avatar} alt={user.name} className="w-full h-full object-cover" />
                      ) : (
                        <div className={`w-full h-full flex items-center justify-center text-sm font-medium ${
                          isDarkMode ? 'bg-gray-600 text-white' : 'bg-gray-300 text-gray-700'
                        }`}>
                          {user.name.charAt(0).toUpperCase()}
                        </div>
                      )}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className={`text-sm font-medium truncate ${isDarkMode ? 'text-white' : 'text-gray-800'}`}>
                        {user.name}
                      </p>
                      <p className={`text-xs ${isDarkMode ? 'text-gray-400' : 'text-gray-500'}`}>
                        已登录
                      </p>
                    </div>
                    <svg className={`w-4 h-4 ${isDarkMode ? 'text-gray-400' : 'text-gray-500'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    </svg>
                  </>
                ) : (
                  <>
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                      isDarkMode ? 'bg-gray-600 text-gray-300' : 'bg-gray-200 text-gray-600'
                    }`}>
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                      </svg>
                    </div>
                    <div className="flex-1">
                      <p className={`text-sm font-medium ${isDarkMode ? 'text-white' : 'text-gray-800'}`}>
                        请登录
                      </p>
                      <p className={`text-xs ${isDarkMode ? 'text-gray-400' : 'text-gray-500'}`}>
                        登录以同步数据
                      </p>
                    </div>
                    <svg className={`w-4 h-4 ${isDarkMode ? 'text-gray-400' : 'text-gray-500'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                    </svg>
                  </>
                )}
              </div>
            </div>
          </div>
        </div>
        
        {/* 主要内容区域 */}
        <div className="flex-1 flex flex-col">
          {/* 顶部工具栏 */}
          <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border-b p-4`}>
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <button
                  onClick={() => setIsSidebarOpen(!isSidebarOpen)}
                  className={`p-2 rounded-lg ${isDarkMode ? 'hover:bg-gray-700' : 'hover:bg-gray-100'}`}
                >
                  <span className={`text-xl ${isDarkMode ? 'text-white' : 'text-gray-700'}`}>
                    {isSidebarOpen ? '◀' : '▶'}
                  </span>
                </button>
                <h1 className={`text-xl font-semibold ${isDarkMode ? 'text-white' : 'text-gray-800'}`}>
                  {currentConversation?.title || 'AI Assistant'}
                </h1>
              </div>
              
              {/* 主题切换按钮 */}
              <button
                onClick={toggleTheme}
                className={`p-2 rounded-lg ${isDarkMode ? 'bg-gray-700 text-yellow-400' : 'bg-gray-100 text-gray-600'} hover:opacity-80`}
              >
                {isDarkMode ? '🌙' : '☀️'}
              </button>
            </div>
          </div>
          
          {/* 消息显示区域 */}
          <div className="flex-1 overflow-y-auto p-4">
            {currentConversation && (
              <div className="max-w-4xl mx-auto space-y-4">
                {currentConversation.messages.map((msg) => (
                  <div key={msg.id} className={`flex ${msg.isUser ? 'justify-end' : 'justify-start'}`}>
                    <div className={`max-w-xl px-4 py-3 rounded-lg ${
                      msg.isUser 
                        ? 'bg-blue-500 text-white' 
                        : (isDarkMode ? 'bg-gray-800 text-white' : 'bg-white text-gray-800 border border-gray-200')
                    } shadow-xs`}>
                      <div 
                        className={`${msg.isUser ? 'text-white' : (isDarkMode ? 'text-white' : 'text-gray-800')}`}
                        dangerouslySetInnerHTML={{ __html: renderMarkdown(msg.content, msg.isUser) }}
                      />
                      <p className={`text-xs mt-2 ${
                        msg.isUser ? 'text-blue-100' : (isDarkMode ? 'text-gray-400' : 'text-gray-500')
                      }`}>
                        {msg.timestamp.toLocaleTimeString()}
                      </p>
                    </div>
                  </div>
                ))}
                
                {isLoading && (
                  <div className="flex justify-start">
                    <div className={`max-w-xl px-4 py-3 rounded-lg ${isDarkMode ? 'bg-gray-800' : 'bg-white border border-gray-200'} shadow-xs`}>
                      <div className="flex items-center space-x-2">
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                        <span className={`text-sm ${isDarkMode ? 'text-gray-400' : 'text-gray-500'}`}>AI is thinking...</span>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
          
          {/* 消息输入区域 */}
          <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border-t p-4`}>
            <div className="max-w-4xl mx-auto">
              {/* 整个输入区域的边框包装 */}
              <div 
                className={`border rounded-lg ${
                  isDarkMode ? 'border-gray-600 bg-gray-800' : 'border-gray-300 bg-white'
                } ${isDragOver ? 'border-blue-400 bg-blue-50 dark:bg-blue-900/20' : ''} transition-colors`}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
              >
                {/* 1. 文件上传区域（上部 - 极致紧凑） */}
                <div className={`px-4 py-0.5 ${
                  selectedFiles.length > 0 || isDragOver ? 'border-b' : ''
                } ${isDarkMode ? 'border-gray-600' : 'border-gray-200'}`}>
                  {/* 文件上传按钮和待上传文件列表 - 在一行显示，超出自动换行 */}
                  <div className="flex items-center flex-wrap gap-x-1 gap-y-0.5">
                    {/* 文件上传按钮 - 添加悬停高亮效果 */}
                    <div className="relative">
                      <input
                        type="file"
                        multiple
                        onChange={(e) => {
                          const files = Array.from(e.target.files || []);
                          handleFileSelect(files);
                          e.target.value = '';
                        }}
                        className="hidden"
                        id="file-upload"
                        accept="image/*,.pdf,.doc,.docx,.txt,.csv,.xlsx,.xls"
                      />
                      <label
                        htmlFor="file-upload"
                        className={`inline-flex items-center px-2 py-1 rounded cursor-pointer transition-colors ${
                          isDarkMode 
                            ? 'text-gray-400 hover:text-gray-300 hover:bg-gray-700' 
                            : 'text-gray-600 hover:text-gray-700 hover:bg-gray-100'
                        }`}
                        title="添加文件"
                      >
                        <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={2}>
                          <path strokeLinecap="round" strokeLinejoin="round" d="M21.44 11.05l-9.19 9.19a6 6 0 01-8.49-8.49l9.19-9.19a4 4 0 015.66 5.66L9.64 16.2a2 2 0 11-2.83-2.83l8.49-8.49" />
                        </svg>
                      </label>
                    </div>

                    {/* 待上传文件列表 - 添加悬停高亮效果 */}
                    {selectedFiles.map((file, index) => (
                      <div 
                        key={index}
                        className={`flex items-center gap-x-0.5 px-2 py-1 rounded text-xs transition-colors ${
                          isDarkMode 
                            ? 'text-gray-300 hover:bg-gray-700' 
                            : 'text-gray-600 hover:bg-gray-100'
                        }`}
                      >
                        <span className="text-xs">{getFileIcon(file)}</span>
                        <span className="font-medium truncate max-w-[80px]" title={file.name}>
                          {file.name}
                        </span>
                        <span className={`text-[9px] ${isDarkMode ? 'text-gray-400' : 'text-gray-500'}`}>({(file.size / 1024).toFixed(0)}K)</span>
                        <button
                          onClick={() => removeFile(index)}
                          className={`p-0.5 rounded text-red-500 hover:text-red-600 transition-colors ${
                            isDarkMode 
                              ? 'hover:bg-red-900/20' 
                              : 'hover:bg-red-50'
                          }`}
                          title="移除文件"
                        >
                          <svg className="w-2 h-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                          </svg>
                        </button>
                      </div>
                    ))}
                  </div>

                  {/* 拖拽上传提示 */}
                  {isDragOver && (
                    <div className={`mt-2 p-3 border-2 border-dashed rounded-lg text-center ${
                      isDarkMode 
                        ? 'border-blue-400 bg-blue-900/20 text-blue-300' 
                        : 'border-blue-400 bg-blue-50 text-blue-600'
                    }`}>
                      <svg className="w-5 h-5 mx-auto mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                      </svg>
                      <p className="text-xs font-medium">拖拽文件到此处上传</p>
                      <p className="text-[10px] mt-0.5">支持图片、文档等多种格式，最大10MB</p>
                    </div>
                  )}
                </div>
                
                {/* 2. 文字输入和发送按钮区域（中部 - 绿色框区域） */}
                <div className="px-4 py-3">
                  <div className="flex items-end space-x-3">
                    <textarea
                      ref={textareaRef}
                      value={message}
                      onChange={handleMessageChange}
                      onKeyDown={(e: any) => {
                        if (e.key === 'Enter' && e.ctrlKey) {
                          e.preventDefault();
                          sendMessage();
                        }
                      }}
                      onFocus={() => {
                        // 这个回调函数可以帮助解决焦点问题
                        // 当输入框获得焦点时，设置messageJustSent为false
                        if (messageJustSent) {
                          setMessageJustSent(false);
                        }
                      }}
                      placeholder="输入消息... (Ctrl+Enter 发送)"
                      rows={1}
                      className={`flex-1 px-0 py-2 resize-none min-h-8 max-h-[200px] overflow-y-auto border-none outline-hidden ${
                        isDarkMode 
                          ? 'bg-transparent text-white placeholder-gray-400' 
                          : 'bg-transparent text-gray-900 placeholder-gray-500'
                      }`}
                      disabled={isLoading}
                    />
                    
                    {/* Send/Cancel 按钮 */}
                    <button
                      onClick={isLoading ? cancelRequest : sendMessage}
                      disabled={!isLoading && (!message.trim() && selectedFiles.length === 0)}
                      className={`p-2 rounded-md transition-colors ${
                        !isLoading && (!message.trim() && selectedFiles.length === 0)
                          ? isDarkMode ? 'text-gray-600' : 'text-gray-400'
                          : isLoading
                            ? isDarkMode 
                              ? 'text-red-400 hover:text-red-300 hover:bg-gray-700' 
                              : 'text-red-600 hover:text-red-700 hover:bg-gray-100'
                            : isDarkMode 
                              ? 'text-blue-400 hover:text-blue-300 hover:bg-gray-700' 
                              : 'text-blue-600 hover:text-blue-700 hover:bg-gray-100'
                      }`}
                      title={isLoading ? "取消生成" : "发送消息"}
                    >
                      {isLoading ? (
                        <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                          <rect x="6" y="6" width="12" height="12" rx="2" ry="2"/>
                        </svg>
                      ) : (
                        <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                          <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
                        </svg>
                      )}
                    </button>
                    
                    {/* New Chat 按钮 */}
                    <button
                      onClick={createNewConversation}
                      className={`p-2 rounded-md transition-colors ${
                        isDarkMode 
                          ? 'text-gray-400 hover:text-white hover:bg-gray-700' 
                          : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                      }`}
                      title="新建对话"
                    >
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                      </svg>
                    </button>
                  </div>
                </div>
                
                {/* 3. 对话设置工具栏（底部） */}
                <div className={`px-4 py-2 border-t ${isDarkMode ? 'border-gray-600' : 'border-gray-200'} flex items-center justify-between`}>
                  <div className="flex items-center space-x-2">
                    {/* 模型选择下拉框 */}
                    <select
                      value={selectedModel}
                      onChange={(e) => setSelectedModel(e.target.value)}
                      className={`text-xs px-1.5 py-1 rounded border-none outline-hidden ${
                        isDarkMode 
                          ? 'bg-transparent text-gray-300 hover:bg-gray-700' 
                          : 'bg-transparent text-gray-700 hover:bg-gray-100'
                      }`}
                    >
                      <option value="gpt-4">Claude Sonnet 4</option>
                      <option value="gpt-3.5">GPT-3.5 Turbo</option>
                      <option value="claude">Claude</option>
                    </select>
                    
                    {/* 模型设置按钮 */}
                    <button
                      className={`p-1 rounded-md transition-colors ${
                        isDarkMode 
                          ? 'text-gray-400 hover:text-white hover:bg-gray-700' 
                          : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                      }`}
                      title="模型设置"
                    >
                      <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      </svg>
                    </button>
                    
                    {/* 警告按钮 */}
                    <button
                      className={`p-1 rounded-md transition-colors ${
                        isDarkMode 
                          ? 'text-yellow-400 hover:text-yellow-300 hover:bg-gray-700' 
                          : 'text-yellow-600 hover:text-yellow-700 hover:bg-gray-100'
                      }`}
                      title="注意事项"
                    >
                      <svg className="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z"/>
                      </svg>
                    </button>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    {/* 语音输入按钮（未来功能） */}
                    <button
                      className={`p-1 rounded-md transition-colors ${
                        isDarkMode 
                          ? 'text-gray-400 hover:text-white hover:bg-gray-700' 
                          : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                      }`}
                      title="语音输入"
                    >
                      <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                      </svg>
                    </button>
                    
                    {/* 更多选项按钮 */}
                    <button
                      className={`p-1 rounded-md transition-colors ${
                        isDarkMode 
                          ? 'text-gray-400 hover:text-white hover:bg-gray-700' 
                          : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                      }`}
                      title="更多选项"
                    >
                      <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 12h.01M12 12h.01M19 12h.01M6 12a1 1 0 11-2 0 1 1 0 012 0zm7 0a1 1 0 11-2 0 1 1 0 012 0zm7 0a1 1 0 11-2 0 1 1 0 012 0z" />
                      </svg>
                    </button>
                  </div>
                </div>
              </div>
              
              {/* 使用提示 */}
              <p className={`text-xs mt-2 ${isDarkMode ? 'text-gray-400' : 'text-gray-500'}`}>
                支持拖拽文件上传 • 按 Enter 换行，按 Ctrl+Enter 发送消息 • 按 Ctrl+V 粘贴截图/文件
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}