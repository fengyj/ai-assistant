import { mockConversations } from '../../utils/mockData';
import React, { useState, useEffect } from 'react';
import { 
  UserIcon, 
  ArrowRightOnRectangleIcon,
  EllipsisVerticalIcon
} from '@heroicons/react/24/outline';
import { 
  Bars3Icon
} from '@heroicons/react/24/outline';
import { useSidebar } from '../../hooks/useSidebar';
import { isAuthenticated, getUserInfo, logout } from '../../utils/auth';
import { useNavigate } from 'react-router-dom';

interface SidebarProps {
  className?: string;
}

const Sidebar: React.FC<SidebarProps> = ({ className = '' }) => {
  const { isCollapsed, toggleCollapse } = useSidebar();
  const [authenticated, setAuthenticated] = useState(isAuthenticated());
  const [userInfo, setUserInfo] = useState(getUserInfo());
  const [showLogoutDialog, setShowLogoutDialog] = useState(false);
  const [openMenuId, setOpenMenuId] = useState<string | null>(null);
  const navigate = useNavigate();
  
  // 监听认证状态变化
  useEffect(() => {
    const handleAuthChange = () => {
      setAuthenticated(isAuthenticated());
      setUserInfo(getUserInfo());
    };

    // 监听新的authChanged事件
    window.addEventListener('authChanged', handleAuthChange);
    // 保持对旧事件的兼容性
    window.addEventListener('authStateChanged', handleAuthChange);
    window.addEventListener('tokenChanged', handleAuthChange);
    
    return () => {
      window.removeEventListener('authChanged', handleAuthChange);
      window.removeEventListener('authStateChanged', handleAuthChange);
      window.removeEventListener('tokenChanged', handleAuthChange);
    };
  }, []);

  // 处理登出按钮点击
  const handleLogoutClick = () => {
    setShowLogoutDialog(true);
  };

  // 处理登出确认
  const handleLogoutConfirm = () => {
    logout();
    setShowLogoutDialog(false);
    navigate('/login');
  };

  // 处理登出取消
  const handleLogoutCancel = () => {
    setShowLogoutDialog(false);
  };

  // 处理菜单按钮点击
  const handleMenuClick = (conversationId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    setOpenMenuId(openMenuId === conversationId ? null : conversationId);
  };

  // 处理重命名
  const handleRename = (conversationId: string) => {
    console.log('重命名对话:', conversationId);
    setOpenMenuId(null);
  };

  // 处理删除
  const handleDelete = (conversationId: string) => {
    console.log('删除对话:', conversationId);
    setOpenMenuId(null);
  };

  // 点击对话框外部关闭
  const handleDialogBackdropClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      setShowLogoutDialog(false);
    }
  };

  // 监听ESC键关闭对话框和点击外部关闭菜单
  useEffect(() => {
    const handleEscKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        if (showLogoutDialog) {
          setShowLogoutDialog(false);
        } else if (openMenuId) {
          setOpenMenuId(null);
        }
      }
    };

    const handleClickOutside = (e: MouseEvent) => {
      if (openMenuId) {
        const target = e.target as Element;
        if (!target.closest('.conversation-options-btn') && !target.closest('.conversation-menu')) {
          setOpenMenuId(null);
        }
      }
    };

    if (showLogoutDialog) {
      document.addEventListener('keydown', handleEscKey);
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }

    if (openMenuId) {
      document.addEventListener('keydown', handleEscKey);
      document.addEventListener('click', handleClickOutside);
    }

    return () => {
      document.removeEventListener('keydown', handleEscKey);
      document.removeEventListener('click', handleClickOutside);
      document.body.style.overflow = 'unset';
    };
  }, [showLogoutDialog, openMenuId]);
  
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
                  <div key={conv.id} className="conversation-item">
                    <div className="conversation-title">
                      {conv.title}
                    </div>
                    <div className="relative">
                      <button 
                        className="conversation-options-btn"
                        title="更多操作"
                        onClick={(e) => handleMenuClick(conv.id, e)}
                      >
                        <EllipsisVerticalIcon className="w-4 h-4" />
                      </button>
                      
                      {/* 下拉菜单 */}
                      {openMenuId === conv.id && (
                        <div className="conversation-menu right-0">
                          <button
                            className="conversation-menu-item"
                            onClick={() => handleRename(conv.id)}
                          >
                            重命名
                          </button>
                          <button
                            className="conversation-menu-item danger"
                            onClick={() => handleDelete(conv.id)}
                          >
                            删除
                          </button>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* 底部：用户状态栏 */}
      <div className="user-status">
        {authenticated ? (
          <div className="user-status-content">
            <div className="user-avatar">
              <UserIcon className="w-5 h-5 text-gray-600 dark:text-gray-400" />
            </div>
            {!isCollapsed && (
              <div className="user-info">
                <div className="user-name">
                  {userInfo?.display_name || userInfo?.username || '用户'}
                </div>
                <div className="user-status-text">
                  {userInfo?.role === 'admin' ? '管理员' : '已登录'}
                </div>
              </div>
            )}
            {!isCollapsed && (
              <button
                onClick={handleLogoutClick}
                className="logout-btn group flex-shrink-0 ml-auto"
                title="登出"
              >
                <ArrowRightOnRectangleIcon className="w-4 h-4 text-gray-500 group-hover:text-red-600 dark:group-hover:text-red-400 transition-colors" />
              </button>
            )}
          </div>
        ) : (
          <div className="user-status-content">
            <div className="user-avatar">
              <UserIcon className="w-5 h-5 text-gray-400" />
            </div>
            {!isCollapsed && (
              <div className="user-info">
                <div className="user-name text-gray-500">未登录</div>
                <div className="user-status-text">点击登录</div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* 登出确认对话框 */}
      {showLogoutDialog && (
        <div 
          className="modal-overlay"
          onClick={handleDialogBackdropClick}
        >
          <div 
            className="modal-content p-6 w-80 max-w-sm mx-4 shadow-2xl border border-gray-200 dark:border-gray-700"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center mb-4">
              <div className="icon-container w-10 h-10 bg-red-100 dark:bg-red-900/30 rounded-full mr-3">
                <ArrowRightOnRectangleIcon className="w-5 h-5 text-red-600 dark:text-red-400" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                确认登出
              </h3>
            </div>
            <p className="text-gray-600 dark:text-gray-300 mb-6 leading-relaxed">
              您确定要登出当前账户吗？
            </p>
            <div className="flex space-x-3">
              <button
                onClick={handleLogoutCancel}
                className="flex-1 px-4 py-2.5 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 dark:focus:ring-offset-gray-900 transition-colors font-medium"
              >
                取消
              </button>
              <button
                onClick={handleLogoutConfirm}
                className="flex-1 px-4 py-2.5 border border-red-600 text-red-600 dark:text-red-400 bg-transparent hover:bg-red-600 hover:text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 dark:focus:ring-offset-gray-900 transition-colors font-medium"
              >
                确认登出
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Sidebar;
