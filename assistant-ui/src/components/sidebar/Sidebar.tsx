import { mockConversations } from '../../utils/mockData';
import React from 'react';
import { 
  UserIcon, 
  TrashIcon
} from '@heroicons/react/24/outline';
import { 
  Bars3Icon
} from '@heroicons/react/24/outline';
import { useSidebar } from '../../hooks/useSidebar';

interface SidebarProps {
  className?: string;
}

export const Sidebar: React.FC<SidebarProps> = ({ className = '' }) => {
  const { isCollapsed, toggleCollapse } = useSidebar();
  
  // 模拟对话历史数据
  const conversations = mockConversations;

  const groupedConversations = conversations.reduce((groups, conv) => {
    const group = conv.group;
    if (!groups[group]) {
      groups[group] = [];
    }
    groups[group].push(conv);
    return groups;
  }, {} as Record<string, typeof conversations>);

  return (
    <div className={`sidebar ${className} ${isCollapsed ? 'collapsed' : ''}`}>
      {/* 侧边栏头部 - 汉堡折叠按钮 */}
      <div className="sidebar-header">
        <button
          onClick={toggleCollapse}
          className="sidebar-collapse-btn"
          title={isCollapsed ? '展开侧边栏' : '折叠侧边栏'}
        >
          <Bars3Icon className="w-5 h-5" />
        </button>
        {!isCollapsed && (
          <h1 className="sidebar-title">对话历史</h1>
        )}
      </div>

      {/* 顶部：历史对话列表 - 折叠时隐藏 */}
      {!isCollapsed && (
        <div className="sidebar-content">
          {Object.entries(groupedConversations).map(([group, convs]) => (
            <div key={group} className="conversation-group">
              <h3 className="sidebar-group-title">
                {group}
              </h3>
              <div className="conversation-list">
                {convs.map((conv) => (
                  <div
                    key={conv.id}
                    className="conversation-item group"
                  >
                    <div className="conversation-info">
                      <p className="conversation-title">
                        {conv.title}
                      </p>
                      <p className="conversation-time">
                        {conv.time}
                      </p>
                    </div>
                    <button className="conversation-delete-btn" title="删除对话">
                      <TrashIcon className="w-3.5 h-3.5" />
                    </button>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* 底部：用户状态栏，始终在底部显示 */}
      <div className="user-status" style={{ marginTop: 'auto' }}>
        <div className="user-status-content">
          <div className="user-avatar">
            <UserIcon className="w-5 h-5 text-gray-600 dark:text-gray-400" />
          </div>
          {!isCollapsed && (
            <div className="user-info">
              <p className="user-name">
                未登录
              </p>
              <p className="user-status-text">
                点击登录
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
