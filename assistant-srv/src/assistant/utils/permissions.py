"""
Permission decorators for API endpoints.
Centralizes authorization logic following DRY principle.
"""

from functools import wraps
from typing import Any, Callable, Optional

from fastapi import HTTPException, status

from ..models.user import User


def _extract_user_from_kwargs(**kwargs: Any) -> Optional[User]:
    """Extract current_user from FastAPI dependencies in kwargs."""
    for key, value in kwargs.items():
        if hasattr(value, "role") and hasattr(value, "id"):
            return value  # type: ignore[no-any-return]
    return None


def _get_user_role(current_user: User) -> str:
    """Get user role as string."""
    return current_user.role.value if hasattr(current_user.role, "value") else str(current_user.role)


def require_admin(func: Callable[..., Any]) -> Callable[..., Any]:
    """装饰器：要求管理员权限"""

    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        current_user = _extract_user_from_kwargs(**kwargs)

        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required",
            )

        user_role = _get_user_role(current_user)

        if user_role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Admin role required",
            )

        return await func(*args, **kwargs)

    return wrapper


def require_owner(func: Callable[..., Any]) -> Callable[..., Any]:
    """装饰器：要求用户是目标用户本人"""

    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        current_user = _extract_user_from_kwargs(**kwargs)

        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required",
            )

        # 获取目标用户ID
        target_user_id = kwargs.get("user_id")
        if target_user_id is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User ID required")

        # 检查是否是用户本人
        if current_user.id != target_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: You can only access your own resources",
            )

        return await func(*args, **kwargs)

    return wrapper


def require_owner_or_admin(func: Callable[..., Any]) -> Callable[..., Any]:
    """装饰器：要求用户是目标用户本人或管理员"""

    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        current_user = _extract_user_from_kwargs(**kwargs)

        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required",
            )

        user_role = _get_user_role(current_user)

        # 如果是管理员，直接放行
        if user_role == "admin":
            return await func(*args, **kwargs)

        # 获取目标用户ID
        target_user_id = kwargs.get("user_id")
        if target_user_id is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User ID required")

        # 检查是否是用户本人
        if current_user.id != target_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: You can only access your own resources",
            )

        return await func(*args, **kwargs)

    return wrapper


def require_session_owner_or_admin(func: Callable[..., Any]) -> Callable[..., Any]:
    """装饰器：要求用户是会话所有者或管理员"""

    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        current_user = _extract_user_from_kwargs(**kwargs)

        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required",
            )

        user_role = _get_user_role(current_user)

        # 如果是管理员，直接放行
        if user_role == "admin":
            return await func(*args, **kwargs)

        # 从参数中获取会话
        session = kwargs.get("session")
        if session is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Session required")

        # 检查是否是会话所有者
        if session.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: You can only access your own sessions",
            )

        return await func(*args, **kwargs)

    return wrapper


def require_session_token_owner_or_admin(func: Callable[..., Any]) -> Callable[..., Any]:
    """装饰器：要求会话所有者或管理员权限（针对session token的特殊装饰器）"""

    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        from ..repositories.json_session_repository import JsonSessionRepository
        from ..services.session_service import SessionService

        current_user = _extract_user_from_kwargs(**kwargs)
        token = kwargs.get("token")

        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required",
            )

        if not token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing token parameter",
            )

        user_role = _get_user_role(current_user)

        if user_role == "admin":
            return await func(*args, **kwargs)

        # 验证会话归属
        session_repo = JsonSessionRepository("data/sessions.json")
        session_service = SessionService(session_repo)
        session = await session_service.get_session_by_token(token)

        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found or expired",
            )

        if session.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: You can only access your own sessions",
            )

        return await func(*args, **kwargs)

    return wrapper
