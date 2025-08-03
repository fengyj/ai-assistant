import { type FC } from 'react';
import type { Conversation, User } from '../types';
import { groupConversationsByTime } from '../utils/conversationUtils';

interface SidebarProps {
  isOpen: boolean;
  conversations: Conversation[];
  currentConversationId: string | null;
  user: User | null;
  onConversationSelect: (id: string) => void;
  onConversationDelete: (id: string) => void;
  onUserStatusClick: () => void;
}

export const Sidebar: FC<SidebarProps> = ({
  isOpen,
  conversations,
  currentConversationId,
  user,
  onConversationSelect,
  onConversationDelete,
  onUserStatusClick
}) => {
  const groupedConversations = groupConversationsByTime(conversations);

  return (
    <div className={`sidebar ${isOpen ? 'open' : 'closed'}`}>
      <div className="p-4 flex flex-col flex-1 min-h-0">
        <div className="sidebar-header">
          <h2 className="sidebar-title">AI Assistant</h2>
        </div>
        
        <div className="sidebar-content">
          <h3 className="sidebar-section-title">对话历史</h3>
          <div className="sidebar-conversations custom-scrollbar">
            {Object.keys(groupedConversations).length === 0 ? (
              <div className="empty-state">
                <div className="empty-state-icon">💬</div>
                <p className="empty-state-text">暂无对话历史</p>
              </div>
            ) : (
              Object.entries(groupedConversations).map(([groupName, groupConversations]) => (
                <div key={groupName}>
                  <h4 className="conversation-group-title">{groupName}</h4>
                  <div className="conversation-list">
                    {groupConversations.map(conv => (
                      <div
                        key={conv.id}
                        className={`conversation-item ${
                          currentConversationId === conv.id ? 'active' : ''
                        }`}
                        onClick={() => onConversationSelect(conv.id)}
                      >
                        <div className="conversation-content">
                          <div className="conversation-info">
                            <p className="conversation-title">{conv.title}</p>
                            <p className="conversation-date">
                              {conv.createdAt.toLocaleDateString('zh-CN', { 
                                month: 'short', 
                                day: 'numeric',
                                hour: '2-digit',
                                minute: '2-digit'
                              })}
                            </p>
                          </div>
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              onConversationDelete(conv.id);
                            }}
                            className="conversation-delete"
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
        <div className="user-status" onClick={onUserStatusClick}>
          <div className="user-status-content">
            {user ? (
              <>
                <div className="user-avatar">
                  {user.avatar ? (
                    <img src={user.avatar} alt={user.name} className="user-avatar-img" />
                  ) : (
                    <div className="user-avatar-fallback">
                      {user.name.charAt(0).toUpperCase()}
                    </div>
                  )}
                </div>
                <div className="user-info">
                  <p className="user-name">{user.name}</p>
                  <p className="user-status-text">已登录</p>
                </div>
                <svg className="user-status-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
              </>
            ) : (
              <>
                <div className="user-avatar">
                  <div className="user-avatar-placeholder">
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                    </svg>
                  </div>
                </div>
                <div className="user-info">
                  <p className="user-name">请登录</p>
                  <p className="user-status-text">登录以同步数据</p>
                </div>
                <svg className="user-status-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;
