# 用户管理模块

根据 readme.md 的要求，用户管理模块已经完整实现，包含以下核心功能：

## 核心功能

### ✅ 已实现的功能

1. **用户注册和认证**
   - 用户名/邮箱 + 密码注册
   - 用户登录验证
   - 密码哈希存储（使用 bcrypt）
   - 密码修改功能

2. **OAuth 认证支持**
   - Google OAuth 登录
   - Microsoft OAuth 登录
   - Apple OAuth 登录
   - OAuth 账户关联/解绑

3. **用户资料管理**
   - 显示名称、头像、个人简介
   - 时区、语言设置
   - 个人偏好设置

4. **多用户会话处理**
   - 会话创建和管理
   - 会话令牌验证
   - 会话过期处理
   - 多设备会话支持

5. **用户状态管理**
   - 用户状态（活跃/非活跃/暂停）
   - 用户角色（管理员/普通用户/访客）
   - 权限系统基础架构

## 项目结构

```
assistant-srv/src/assistant/
├── api/
│   ├── users.py          # 用户管理 API 端点
│   ├── oauth.py          # OAuth 认证 API 端点
│   └── sessions.py       # 会话管理 API 端点
├── models/
│   ├── user.py           # 用户数据模型
│   └── session.py        # 会话数据模型
├── services/
│   ├── user_service.py   # 用户业务逻辑服务
│   └── session_service.py # 会话业务逻辑服务
├── repositories/
│   ├── base.py                    # 基础存储库接口
│   ├── user_repository.py         # 用户存储库接口
│   ├── json_user_repository.py    # JSON 用户存储实现
│   ├── session_repository.py      # 会话存储库接口
│   └── json_session_repository.py # JSON 会话存储实现
├── core/
│   ├── config.py         # 配置管理
│   └── exceptions.py     # 自定义异常
└── utils/
    ├── security.py       # 密码哈希和令牌生成
    └── db_init.py        # 数据库初始化
```

## API 端点

### 用户管理 API (`/api/users`)

- `POST /api/users/` - 创建新用户
- `GET /api/users/{user_id}` - 根据 ID 获取用户
- `GET /api/users/` - 获取所有用户
- `PUT /api/users/{user_id}` - 更新用户信息
- `DELETE /api/users/{user_id}` - 删除用户
- `POST /api/users/login` - 用户登录
- `POST /api/users/{user_id}/change-password` - 修改密码
- `GET /api/users/search/{query}` - 搜索用户

### OAuth 认证 API (`/api/oauth`)

- `GET /api/oauth/{provider}/authorize` - 获取 OAuth 授权 URL
- `POST /api/oauth/{provider}/callback` - 处理 OAuth 回调
- `POST /api/oauth/{provider}/unlink/{user_id}` - 解绑 OAuth 提供商

### 会话管理 API (`/api/sessions`)

- `POST /api/sessions/` - 创建会话
- `GET /api/sessions/{token}` - 根据令牌获取会话
- `GET /api/sessions/user/{user_id}` - 获取用户会话
- `POST /api/sessions/{token}/refresh` - 刷新会话
- `DELETE /api/sessions/{token}` - 终止会话
- `DELETE /api/sessions/user/{user_id}/all` - 终止用户所有会话
- `POST /api/sessions/cleanup` - 清理过期会话
- `POST /api/sessions/{token}/validate` - 验证会话

## 快速开始

### 1. 启动服务器

```bash
cd assistant-srv
python run_server.py
```

服务器将在 `http://localhost:8000` 启动，并自动：
- 创建数据目录
- 初始化默认管理员账户（admin/admin123）

### 2. 查看 API 文档

访问 `http://localhost:8000/docs` 查看 Swagger API 文档

### 3. 创建用户示例

```bash
# 创建新用户
curl -X POST "http://localhost:8000/api/users/" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "securepass123",
    "display_name": "Test User"
  }'

# 用户登录
curl -X POST "http://localhost:8000/api/users/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "securepass123"
  }'
```

### 4. 创建会话

```bash
# 创建会话
curl -X POST "http://localhost:8000/api/sessions/" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "用户ID",
    "device_info": "Web Browser"
  }'
```

## 数据存储

目前使用 JSON 文件存储：
- `data/users.json` - 用户数据
- `data/sessions.json` - 会话数据

这种设计易于迁移到其他数据库（PostgreSQL、MongoDB 等）。

## 安全特性

1. **密码安全**
   - 使用 bcrypt 进行密码哈希
   - 不存储明文密码

2. **会话安全**
   - 随机生成的会话令牌
   - 会话过期机制
   - 会话验证

3. **数据验证**
   - 输入数据验证
   - 邮箱格式验证
   - 用户名唯一性检查

## 测试

运行集成测试：

```bash
cd assistant-srv
python -m pytest tests/test_user_management_integration.py -v
```

## 配置

环境变量配置（可选）：

```bash
export HOST=localhost
export PORT=8000
export DEBUG=true
export DATA_DIR=data
export SECRET_KEY=your-secret-key
export GOOGLE_CLIENT_ID=your-google-client-id
export GOOGLE_CLIENT_SECRET=your-google-client-secret
# ... 其他 OAuth 配置
```

## 扩展性

该用户管理模块设计为可扩展的：

1. **存储层**：可以轻松替换为 PostgreSQL、MongoDB 等
2. **认证方式**：可以添加更多 OAuth 提供商
3. **权限系统**：基础架构已就绪，可以扩展细粒度权限
4. **会话管理**：支持多设备、会话监控等高级功能

## 下一步增强功能

readme.md 中提到的增强功能将在后续版本中实现：

- 角色和权限系统详细实现
- 使用分析和统计
- 使用限制和配额管理
- 审计日志
- 性能监控

用户管理模块的核心功能已经完整实现，为 AI 助手系统提供了坚实的用户管理基础。
