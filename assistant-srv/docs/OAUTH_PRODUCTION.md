# OAuth Production Setup Guide

本文档提供了生产环境中配置OAuth认证的详细说明。

## Microsoft OAuth - 头像获取

### 配置要求

1. **权限范围**: 确保在Azure应用注册中包含以下权限：
   ```
   openid profile email User.Read
   ```

2. **环境变量**:
   ```bash
   MICROSOFT_CLIENT_ID=your_app_id
   MICROSOFT_CLIENT_SECRET=your_app_secret
   MICROSOFT_REDIRECT_URI=http://localhost:8000/api/oauth/microsoft/callback
   ```

### 头像处理说明

我们的实现会尝试从Microsoft Graph API获取用户头像：

- **成功**: 返回base64编码的图片数据
- **失败**: 返回null，记录警告日志
- **生产建议**: 将图片上传到云存储服务，返回URL

### 生产优化建议

```python
# 在生产环境中，建议将图片保存到云存储
async def save_avatar_to_storage(image_data: bytes, user_id: str) -> str:
    """保存头像到云存储并返回URL"""
    # 1. 上传到 AWS S3 / Azure Blob / 阿里云OSS
    # 2. 返回公开访问的URL
    # 3. 设置适当的缓存策略
    pass
```

## Apple OAuth - JWT处理

### 配置要求

1. **Apple Developer Account**:
   - 注册Apple Developer账号
   - 创建App ID和Services ID
   - 生成Sign in with Apple私钥

2. **必需文件**:
   ```
   AuthKey_XXXXXXXXXX.p8  # Apple私钥文件
   ```

3. **环境变量**:
   ```bash
   APPLE_CLIENT_ID=your.bundle.identifier
   APPLE_TEAM_ID=YOUR_TEAM_ID
   APPLE_KEY_ID=XXXXXXXXXX
   APPLE_PRIVATE_KEY_PATH=/path/to/AuthKey_XXXXXXXXXX.p8
   ```

### JWT生成和验证

#### 客户端密钥生成
```python
from src.assistant.utils.apple_jwt import AppleJWTGenerator

# 生成客户端密钥
jwt_generator = AppleJWTGenerator(
    team_id="YOUR_TEAM_ID",
    key_id="XXXXXXXXXX", 
    private_key_path="/path/to/AuthKey_XXXXXXXXXX.p8"
)

client_secret = jwt_generator.generate_client_secret("your.bundle.identifier")
```

#### ID Token验证
```python
from src.assistant.utils.apple_jwt import AppleTokenVerifier

# 验证ID Token
verifier = AppleTokenVerifier()
payload = await verifier.verify_id_token(id_token, client_id)
```

### 安全注意事项

1. **私钥保护**: 
   - 私钥文件权限设置为600
   - 不要将私钥提交到版本控制
   - 使用环境变量或密钥管理服务

2. **Token验证**:
   - 生产环境必须验证JWT签名
   - 检查token的过期时间和颁发者
   - 验证audience和其他关键声明

3. **密钥轮换**:
   - 定期轮换Apple私钥
   - 监控Apple公钥更新

## 通用安全建议

### 1. HTTPS要求
```bash
# 生产环境必须使用HTTPS
OAUTH_REDIRECT_URI=https://yourdomain.com/api/oauth/{provider}/callback
```

### 2. 状态参数保护
```python
# 我们的实现已包含CSRF保护
# 状态令牌自动过期，防止重放攻击
```

### 3. 错误处理
```python
# 记录安全相关错误，但不暴露敏感信息给用户
try:
    # OAuth操作
    pass
except Exception as e:
    logger.error(f"OAuth error: {e}")
    raise ValidationError("Authentication failed")
```

### 4. 速率限制
```python
# 建议对OAuth端点实施速率限制
from fastapi_limiter import FastAPILimiter

@app.get("/api/oauth/{provider}/authorize")
@limiter.limit("10/minute")
async def oauth_authorize():
    pass
```

## 监控和日志

### 关键指标
- OAuth成功/失败率
- Token交换延迟
- 用户信息获取成功率
- 头像下载成功率

### 日志记录
```python
# 记录重要的OAuth事件
logger.info(f"OAuth {provider} authorization started for user {user_id}")
logger.info(f"OAuth {provider} successful for user {user_id}")
logger.warning(f"OAuth {provider} failed: {error_message}")
```

## 故障排除

### 常见问题

1. **Microsoft头像获取失败**:
   - 检查权限配置
   - 验证access_token有效性
   - 查看Graph API限制

2. **Apple JWT验证失败**:
   - 确认私钥文件路径正确
   - 检查Team ID和Key ID
   - 验证客户端ID配置

3. **重定向URI不匹配**:
   - 确保环境变量中的URI与提供商配置一致
   - 注意HTTP/HTTPS协议匹配

### 调试工具

```bash
# 测试OAuth配置
python assistant-srv/demo_oauth.py config

# 查看详细错误日志
tail -f /var/log/assistant/oauth.log
```
