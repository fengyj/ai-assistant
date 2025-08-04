## 装饰器名称简化完成

✅ **重命名完成**

### 简化前 → 简化后

- `require_admin_decorator` → `require_admin`
- `require_owner_or_admin_decorator` → `require_owner_or_admin`

### 应用的API端点

```python
# 管理员权限装饰器
@require_admin
- create_user()        # 创建用户
- get_users()          # 获取所有用户
- delete_user()        # 删除用户
- search_users()       # 搜索用户

# 所有者或管理员权限装饰器
@require_owner_or_admin("user_id")
- get_user()           # 获取用户信息
- update_user()        # 更新用户信息
- change_password()    # 修改密码
```

### 优势

1. **名称更简洁**: 去掉了冗余的 `_decorator` 后缀
2. **更符合Python约定**: 装饰器通常不需要显式包含"decorator"词汇
3. **保持功能完整**: 所有权限验证逻辑保持不变
4. **易于使用**: 更短的名称使代码更清晰

### 验证结果

- ✅ 服务器正常运行
- ✅ 权限验证正常工作 (返回403状态码)
- ✅ 所有API端点已更新使用新的装饰器名称
