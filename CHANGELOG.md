
## 2025-08-05

### Fixed

- **修复登录后无法跳转和用户状态栏问题**:
  - 修复了登录成功后页面不跳转到聊天界面的问题
  - 修复了用户状态栏始终显示"未登录"的问题
  - 改进了认证状态管理，使用事件监听机制确保状态同步
  - 添加了JWT token过期检查和用户信息解析功能
  - 在侧边栏添加了动态用户状态显示和登出功能

### Improved

- **增强认证工具函数**:
  - 添加了`getUserInfo()`函数用于从JWT token中提取用户信息
  - 添加了`logout()`函数用于完整的登出处理
  - 改进了token验证逻辑，包含过期检查
  - 添加了自定义事件机制，确保认证状态变化时各组件能够同步更新

- **改进登出用户体验**:
  - 将浏览器原生的`window.confirm`对话框替换为自定义HTML对话框
  - 分离登出按钮，只有点击专门的登出按钮才会触发对话框
  - 登出按钮支持hover状态，图标颜色会从灰色变为红色
  - 重新设计对话框配色，使用更现代的设计语言和更好的主题适配
  - 添加了毛玻璃背景效果和更精致的阴影
  - 支持ESC键和点击背景关闭对话框
  - 提供更直观的用户界面和更好的可访问性

- Refactored API server address configuration: all API calls now use a centralized config and environment variable for backend server address.
- Login page now uses a unified request utility (axios) for backend communication.

# 变更日志

## [Unreleased]

### Fixed

- **修复前端构建错误**: 解决了TypeScript编译错误
  - 修复了从错误文件路径导入Context Provider的问题
  - 正确配置测试环境，解决了@testing-library/jest-dom的toBeInTheDocument方法未定义问题
  - 创建了setupTests.ts文件并更新了jest配置

### Added

- **装饰器模式权限验证系统**: 实现了基于装饰器的API权限验证
  - `@require_admin_decorator`: 要求管理员权限的装饰器
  - `@require_owner_or_admin_decorator`: 要求资源所有者或管理员权限的装饰器
  - 自动从FastAPI依赖注入中提取`current_user`
  - 统一的权限验证逻辑，提高代码可维护性
  - 替换了所有内联权限检查，改为声明式权限验证
- **完整的用户管理模块**: 实现了用户注册、认证、资料管理和多用户会话处理
- **真实可用的OAuth认证系统**: 支持Google、Microsoft、Apple OAuth登录
  - 抽象OAuth提供商架构，便于扩展新的OAuth提供商
  - 安全的状态管理和CSRF保护
  - 真实的HTTP API调用集成（使用httpx）
  - 自动用户资料同步和关联
- **增强的OAuth功能**:
  - **Microsoft OAuth**: 集成Graph API获取用户头像
  - **Apple OAuth**: 完整的JWT处理和ID token验证
  - **生产级安全**: JWT签名验证、token过期检查、密钥管理
- **会话管理系统**: 支持多设备会话、会话过期和安全验证
- **JSON数据存储**: 易于迁移的存储架构，支持未来数据库集成
- **完整的API端点**: 21个用户管理相关的RESTful API端点
- **安全特性**:
  - bcrypt密码哈希
  - OAuth状态令牌防护
  - 会话过期机制
  - 输入数据验证
- **生产环境支持**:
  - Apple JWT工具类（`apple_jwt.py`）
  - Microsoft Graph API集成
  - 完整的错误处理和日志记录
  - 生产环境配置文档

### Updated

- **依赖管理**: 添加httpx、PyJWT、cryptography依赖
- **服务器启动**: 完整的FastAPI后端服务器可正常运行 (<http://localhost:8000>)
- **文档完善**: 新增`OAUTH_PRODUCTION.md`生产环境配置指南
- **项目配置**: 修复pyproject.toml许可证配置，使用现代SPDX格式
- **可扩展架构**: 模块化设计，支持添加新的OAuth提供商和存储后端
- **完整的测试套件**: 集成测试和OAuth系统测试
- **配置文档**: OAuth设置指南和环境变量配置说明

### Changed

- CodeBlock: Copy button now shows a green check icon (√) for 1.2s after copying, instead of a floating green tip. Improved user feedback and accessibility.
- Improved like/dislike button logic: now the color is always green/red when active, and gray when inactive, regardless of hover state.
- Fixed button style so users can easily see which messages are liked/disliked without needing to hover.
- Added updateMessageMetadata to ConversationContext for message metadata updates.
- Ensured UI state and metadata are always in sync for feedback buttons.
- Optimized CSS selectors to avoid !important rules by using higher specificity.
- Added time constants (FEEDBACK_DURATION, ACTION_FEEDBACK_DURATION) to replace magic numbers.
- Enhanced accessibility with aria-pressed and aria-label attributes for like/dislike buttons.
- Added error handling and logging to updateMessageMetadata function.
- Fixed like/dislike button colors to show active state (green/red) immediately without requiring hover.

### Security

- Applied strict security settings for Mermaid rendering

## [Previous entries remain unchanged]
