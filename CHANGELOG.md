## [Unreleased]

### File Structure Refactoring

- **Reorganized CSS files**: Moved main `index.css` from `src/` to `src/styles/` directory for better organization
- **Updated imports**: Updated `main.tsx` to import styles from the new location (`./styles/index.css`)
- **Improved project structure**: Aligned with existing styles organization where other CSS files were already placed in the styles directory

### UI Improvements

- **Login page icon standardization**: Replaced custom SVG loading spinner with Heroicons `ArrowPathIcon` for consistency with the rest of the application
- **Better icon management**: All loading states now use the same standardized icon from the project's icon library

### UI Improvements for Sidebar and Chat Interface

- **Unified header heights**: Fixed alignment between sidebar header and chat header by setting consistent height (h-16)
- **Streamlined conversation history list**:
  - Removed time display from conversation items for cleaner appearance
  - Reduced spacing between conversation items for more compact layout
  - Updated conversation item padding and margins for better visual density
- **Enhanced conversation actions**:
  - Replaced custom SVG with standard Heroicons EllipsisVerticalIcon for consistency
  - Implemented dropdown menu with "Rename" and "Delete" options
  - Added proper styling for menu items with danger state (red color for delete action)
  - Implemented click-outside and ESC key handling for menu dismissal
- **Code improvements**:
  - Cleaned up unused imports and dependencies
  - Enhanced menu interaction logic with proper state management
  - Improved accessibility with proper button titles and keyboard navigation

### Model Management Integration

- Created integrated ModelControl component that combines model selection, token statistics, and settings
- Implemented ModelContext for centralized model state management:
  - Supports loading model list from API with caching
  - Tracks selected model and automatically loads model information
  - Provides hooks for refreshing model data
  - Includes interfaces for future model statistics and performance metrics
- Added ModelInfoModal for displaying detailed model information:
  - Shows basic model info (name, type, owner, description)
  - Displays token usage statistics with progress bar
  - Shows performance metrics (response time, success rate)
  - Includes last used timestamp and refresh functionality
- Added ModelSettingsModal for configuring model parameters:
  - Temperature slider for controlling output randomness
  - Max tokens setting for response length control
  - Top P parameter for vocabulary diversity
  - Reset to defaults functionality
- Integrated ModelProvider into application context hierarchy
- Updated ChatArea to use new ModelControl component instead of separate components
- Added slider styling for model parameter controls
- Created useModel hook for consuming model context throughout the application

### Enhanced Authentication State Management

- Enhanced UserSessionContext to include comprehensive token information:
  - Added `tokenType` field for Authorization header construction
  - Added `expiryTime` field for proactive token refresh timing
  - Added `isTokenExpiringSoon()` method for checking token status
- Implemented proactive token refresh strategy (5 minutes before expiry) instead of reactive 401 handling
- Added automatic token restoration and refresh on application startup
- Enhanced localStorage management to include `token_type` and better expiry handling
- Updated API response interfaces to include `token_type` field
- Created comprehensive utility hooks and functions for authenticated API requests
- Added example component demonstrating advanced authentication features

### Previous Changes

## [Previous Releases]

- Fixed authentication state persistence: users who were previously logged in now correctly bypass login page on window reopen.
- Enhanced UserSessionContext with proper initialization state management and automatic token refresh on app startup.
- Refactored App.tsx to use UserSessionContext directly instead of maintaining separate authentication state.
- Added initialization loading state to prevent premature redirects while authentication is being restored.
- Improved token refresh logic to handle expired tokens during app initialization.
- Removed validateToken API function and related code as backend no longer supports this endpoint.
- Updated AuthAPIDemo component to remove validateToken functionality and UI elements.
- Refactored authentication API structure: moved login function from Login.tsx to auth.ts for better code organization.
- Added comprehensive authentication API functions (login, refreshToken, logout) in auth.ts.
- Enhanced type safety with proper TypeScript interfaces for all authentication endpoints.
- Simplified Login.tsx by removing inline API calls and using centralized auth functions.
- Enhanced UserSessionContext to include token information (accessToken, sessionId, refreshToken method).
- Created utility functions and hooks for authenticated API requests with automatic token refresh.
- Added example component demonstrating UserSessionContext usage for API calls.
- Improved authentication state management by exposing token data through Context API.
- Removed `assistant-srv/data` directory from git tracking; now ignored by `.gitignore`.
- Fixed missing type annotations in `assistant-srv/src/assistant/utils/db_init.py` to pass mypy checks.

# 2025-08-11

- Refactored model get_model API and ModelService.get_model method.
- Service layer now handles user_id and user_role logic for model access and type.
- Improved code comments and endpoint documentation for clarity and maintainability.
# 2025-08-11
- Refactored session management APIs, SessionService, SessionRepository, and JsonSessionRepository.
- All user_id related session queries now consistently use repository methods for searching sessions by user_id.
- Improved code comments and endpoint documentation for clarity and maintainability.
## [2025-08-09] Refactor session creation usage

- Refactored all usages of `SessionService.create_session` to accept `UserSession` directly in `api/auth.py` and `api/oauth.py`.
- Removed unused imports of `SessionCreateRequest` in affected files.
- Ensured IP tracking and device info logic is preserved.
## [2025-08-09] Refactor SessionService.create_session
- Refactored `SessionService.create_session` to accept a `UserSession` instance directly instead of `SessionCreateRequest`.
- Removed unused import of `SessionCreateRequest`.
- Updated docstring for clarity.
- This change improves flexibility and simplifies session creation logic.
## 2025-08-08

### Enhanced

- **完善JWT + Session混合认证架构**:
  - 修复`extract_session_id_from_jwt`方法使用`decode_jwt_token_ignore_expiry`，确保JWT过期时仍能提取session_id
  - 新增`generate_jwt_token_with_user_info`方法支持在JWT中包含用户基本信息
  - JWT默认过期时间调整为15分钟，Session保持30天
  - JWT将包含用户安全信息：username, display_name, role, permissions, status等
  - 实现分级验证：常规API验证JWT+Session有效性，敏感API要求额外验证
  - 支持用户信息更新后强制所有session过期，确保JWT数据一致性

## 2025-08-07

### Changed

- **重构Session架构以优化JWT认证系统**:
  - 移除了`UserSession`模型中的token字段，消除了循环依赖问题
  - **实现IP地址追踪机制** - 将IP地址移到SessionMetadata中仅用于安全分析，不用于验证：
    - `initial_ip`: 记录session创建时的IP地址
    - `last_known_ips`: 追踪最近使用的IP地址列表（最多保留5个）
    - 用户在session有效期内可以合法地变更IP地址，不会影响认证
    - 提供`update_ip_tracking()`方法用于安全审计和异常检测
  - **重构登录流程使用session-based认证**:
    - `POST /api/auth/login` 现在在密码验证成功后创建session并返回JWT token
    - `POST /api/oauth/login` 同样使用session创建流程
    - JWT token包含session_id用于后续的session查找和验证
    - 移除了直接创建access token的旧方式，统一使用session-based认证
  - **优化Session API结构** - 移除冗余的API端点：
    - 移除 `POST /sessions/` (session创建通过login处理)
    - 移除 `POST /{token}/refresh` (token刷新通过auth模块处理)  
    - 移除 `POST /{token}/validate` (每个API调用自动验证)
    - 保留session管理API用于用户设备管理和管理员维护
  - 实现了配置化的JWT系统，支持环境变量配置issuer和算法
  - 重构`SessionService`，将`get_session_by_token`重命名为`get_session_from_jwt`以提升语义准确性
  - 改进了token生成策略，JWT动态生成而非存储在session中
  - 更新了所有认证流程使用新的架构，确保关注点分离
  - 保持了Fernet加密的向后兼容性，同时优先使用JWT
  - 所有API和权限检查均已更新使用新的方法命名

### Fixed

- **全面修复代码质量问题 (Commit: 4430546)**:
  - 修复了155+个flake8和mypy错误，实现完整的代码质量标准合规
  - 添加了pre-commit hooks配置，确保代码质量的持续维护
  - 移除了所有未使用的导入，改善了代码格式和结构
  - 为整个代码库添加了适当的类型注解，提升了类型安全性
  - 配置了mypy的战略性模块覆盖，平衡了严格性和实用性
  - 改进了权限装饰器的类型安全性和可维护性
  - 修复了OAuth提供商的jwt/cryptography库类型兼容性问题
  - 所有pre-commit检查现已通过：black、isort、flake8、mypy

- **批量修复flake8和mypy错误**:
  - 修复了后端Python文件中的所有flake8和mypy错误，包括：
    - 导入顺序、未使用的导入和空行问题
    - OAuth和Apple提供商逻辑的类型注解和类型兼容性问题
    - 删除了未使用的变量，确保所有代码符合项目的lint/type标准
  - 改善了OAuth提供商实现的代码清晰度和可维护性
  - 所有更改均遵循SOLID原则，并在需要的地方用清晰的注释进行了文档说明

## 2025-08-06

### Refactored

- **重构模型服务和仓储层架构**:
  - 将`ModelRepository`从静态方法重构为异步实例方法
  - 创建了`ModelRepository`接口继承自`BaseRepository[Model]`
  - 实现了`JsonModelRepository`作为JSON文件存储的具体实现
  - 重构`ModelService`使用依赖注入接收repository实例
  - 将所有`ModelService`方法改为异步方法
  - 更新API端点使用异步方法和依赖注入模式
  - 遵循SOLID原则，改善代码的可测试性和可维护性
  - 统一了与用户服务相同的架构模式

### Fixed

- **完成后端Python代码类型注解和认证实现**:
  - 为整个后端代码库添加了全面的类型注解，包括API层、服务层、仓储层、工具层和核心模块
  - 修复了API模型类命名不一致的问题，统一使用`*RequestData`/`*ResponseData`命名规范
  - 将所有API端点的认证从虚假的dict实现替换为正确的`CurrentUser`对象认证
  - 删除了不必要的`ModelKeyRepository`类，简化了代码结构
  - 保留了API key管理功能，使用简化的字典存储而非复杂的类结构
  - 修复了模块导入问题，统一了API模型的导入路径

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
