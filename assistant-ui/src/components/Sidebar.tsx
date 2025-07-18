import { type FC } from 'react';
import type { Conversation, User } from '../types';
import { groupConversationsByTime } from '../utils/conversationUtils';

interface SidebarProps {
  isOpen: boolean;
  conversations: Conversation[];
  currentConversationId: string | null;
  user: User | null;
  isDarkMode: boolean;
  onConversationSelect: (id: string) => void;
  onConversationDelete: (id: string) => void;
  onUserStatusClick: () => void;
}

export const Sidebar: FC<SidebarProps> = ({
  isOpen,
  conversations,
  currentConversationId,
  user,
  isDarkMode,
  onConversationSelect,
  onConversationDelete,
  onUserStatusClick
}) => {
  const groupedConversations = groupConversationsByTime(conversations);

  return (
    <div className={`${isOpen ? 'w-80' : 'w-0'} transition-all duration-300 overflow-hidden ${
      isDarkMode ? 'bg-gray-800' : 'bg-white'
    } border-r ${isDarkMode ? 'border-gray-700' : 'border-gray-200'} flex flex-col`}>
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
                  <h4 className={`text-xs font-semibold ${
                    isDarkMode ? 'text-gray-400' : 'text-gray-600'
                  } mb-2 px-1 uppercase tracking-wide`}>
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
                        onClick={() => onConversationSelect(conv.id)}
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex-1 min-w-0">
                            <p className={`text-sm font-medium ${
                              isDarkMode ? 'text-white' : 'text-gray-800'
                            } truncate leading-tight`}>
                              {conv.title}
                            </p>
                            <p className={`text-xs ${
                              isDarkMode ? 'text-gray-400' : 'text-gray-500'
                            } mt-1 leading-tight`}>
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
                            className={`p-1.5 rounded-sm opacity-0 group-hover:opacity-100 transition-opacity duration-200 ${
                              isDarkMode ? 'hover:bg-gray-600 text-gray-400 hover:text-red-400' : 'hover:bg-gray-200 text-gray-500 hover:text-red-500'
                            } shrink-0`}
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
          onClick={onUserStatusClick}
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
  );
};

export default Sidebar;
