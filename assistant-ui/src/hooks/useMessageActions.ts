import { useCallback, useState } from 'react';
import { useConversation } from './useConversation';

// 时间常量
const FEEDBACK_DURATION = 1200; // 1.2s - 复制成功反馈持续时间
const ACTION_FEEDBACK_DURATION = 2000; // 2s - 其他操作反馈持续时间

export interface UseMessageActionsReturn {
  copyMessage: (messageId: string) => Promise<void>;
  editMessage: (messageId: string, newContent: string) => Promise<void>;
  deleteMessage: (messageId: string) => Promise<void>;
  regenerateMessage: (messageId: string) => Promise<void>;
  likeMessage: (messageId: string) => Promise<void>;
  dislikeMessage: (messageId: string) => Promise<void>;
  isProcessing: boolean;
  lastAction: string | null;
  copiedMessageId: string | null;
}

export const useMessageActions = (): UseMessageActionsReturn => {
  const { 
    editMessage: contextEditMessage,
    deleteMessage: contextDeleteMessage,
    regenerateMessage: contextRegenerateMessage,
    getMessageById,
    updateMessageMetadata
  } = useConversation();
  
  const [isProcessing, setIsProcessing] = useState(false);
  const [lastAction, setLastAction] = useState<string | null>(null);
  const [copiedMessageId, setCopiedMessageId] = useState<string | null>(null);

  // 复制消息到剪贴板
  const copyMessage = useCallback(async (messageId: string): Promise<void> => {
    const message = getMessageById(messageId);
    if (!message) return;

    try {
      setIsProcessing(true);
      setLastAction('copy');
      setCopiedMessageId(messageId);
      
      if (navigator.clipboard && window.isSecureContext) {
        await navigator.clipboard.writeText(message.content);
      } else {
        // 降级方案
        const textArea = document.createElement('textarea');
        textArea.value = message.content;
        textArea.style.position = 'fixed';
        textArea.style.left = '-999999px';
        textArea.style.top = '-999999px';
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        document.execCommand('copy');
        textArea.remove();
      }
      
      // 显示成功提示
      console.log('消息已复制到剪贴板');
      
    } catch (error) {
      console.error('复制失败:', error);
    } finally {
      setIsProcessing(false);
      setTimeout(() => {
        setLastAction(null);
        setCopiedMessageId(null);
      }, FEEDBACK_DURATION);
    }
  }, [getMessageById]);

  // 编辑消息
  const editMessage = useCallback(async (messageId: string, newContent: string): Promise<void> => {
    try {
      setIsProcessing(true);
      setLastAction('edit');
      
      await contextEditMessage(messageId, newContent);
      console.log('消息编辑成功');
      
    } catch (error) {
      console.error('编辑失败:', error);
    } finally {
      setIsProcessing(false);
      setTimeout(() => setLastAction(null), ACTION_FEEDBACK_DURATION);
    }
  }, [contextEditMessage]);

  // 删除消息
  const deleteMessage = useCallback(async (messageId: string): Promise<void> => {
    try {
      setIsProcessing(true);
      setLastAction('delete');
      
      await contextDeleteMessage(messageId);
      console.log('消息删除成功');
      
    } catch (error) {
      console.error('删除失败:', error);
    } finally {
      setIsProcessing(false);
      setTimeout(() => setLastAction(null), ACTION_FEEDBACK_DURATION);
    }
  }, [contextDeleteMessage]);

  // 重新生成消息
  const regenerateMessage = useCallback(async (messageId: string): Promise<void> => {
    try {
      setIsProcessing(true);
      setLastAction('regenerate');
      
      await contextRegenerateMessage(messageId);
      console.log('消息重新生成成功');
      
    } catch (error) {
      console.error('重新生成失败:', error);
    } finally {
      setIsProcessing(false);
      setTimeout(() => setLastAction(null), ACTION_FEEDBACK_DURATION);
    }
  }, [contextRegenerateMessage]);

  // 点赞消息
  const likeMessage = useCallback(async (messageId: string): Promise<void> => {
    const message = getMessageById(messageId);
    if (!message) return;
    try {
      setIsProcessing(true);
      setLastAction('like');
      // 切换 liked 状态，取消 disliked
      updateMessageMetadata(messageId, {
        liked: !message.metadata?.liked,
        disliked: false
      });
    } catch (error) {
      console.error('点赞失败:', error);
    } finally {
      setIsProcessing(false);
      setTimeout(() => setLastAction(null), ACTION_FEEDBACK_DURATION);
    }
  }, [getMessageById, updateMessageMetadata]);

  // 点踩消息
  const dislikeMessage = useCallback(async (messageId: string): Promise<void> => {
    const message = getMessageById(messageId);
    if (!message) return;
    try {
      setIsProcessing(true);
      setLastAction('dislike');
      // 切换 disliked 状态，取消 liked
      updateMessageMetadata(messageId, {
        disliked: !message.metadata?.disliked,
        liked: false
      });
    } catch (error) {
      console.error('点踩失败:', error);
    } finally {
      setIsProcessing(false);
      setTimeout(() => setLastAction(null), ACTION_FEEDBACK_DURATION);
    }
  }, [getMessageById, updateMessageMetadata]);

  return {
    copyMessage,
    editMessage,
    deleteMessage,
    regenerateMessage,
    likeMessage,
    dislikeMessage,
    isProcessing,
    lastAction,
    copiedMessageId,
  };
};

export default useMessageActions;
