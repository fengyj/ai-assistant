"""
Database initialization and migration script.
"""

import asyncio
import logging
import os

from ..core import config
from ..core.dependencies import get_model_service
from ..models.model import SYSTEM_OWNER, Model

logger = logging.getLogger(__name__)


def ensure_data_directory() -> None:
    """Ensure data directory exists."""
    os.makedirs(config.data_dir, exist_ok=True)
    logger.info(f"Data directory ensured: {config.data_dir}")


def create_default_admin_user() -> None:
    """Create default admin user if no users exist, using UserService."""

    async def _init_admin() -> None:
        from ..core.dependencies import get_user_service
        from ..models.user import UserCreateRequest, UserRole

        user_service = get_user_service()
        # 检查是否已有用户
        users = await user_service.get_all_users()
        if users:
            logger.info("Users already exist, skipping default admin creation")
            return
        admin_request = UserCreateRequest(
            username="admin",
            email="admin@localhost",
            password="admin123",
            display_name="System Administrator",
            role=UserRole.ADMIN,
        )
        await user_service.create_user(admin_request)

    logger.info("Default admin user created: admin/admin123")

    asyncio.run(_init_admin())


def initialize_models_data() -> None:
    """Initialize model data with default models."""

    async def _init_models() -> None:
        model_service = get_model_service()
        # 检查是否已有系统模型
        system_models = await model_service.list_system_models()
        if system_models:
            logger.info("Model data already exists, skipping initialization.")
            return
        from ..models.model import ModelCapabilities, ModelParams, ProviderInfo

        default_models = [
            Model(
                id="openrouter-deepseek-chat",
                name="OpenRouter DeepSeek Chat",
                description="deepseek-chat-v3-0324:free",
                owner=SYSTEM_OWNER,
                provider=ProviderInfo(
                    model="deepseek/deepseek-chat-v3-0324:free",
                    api_type="openai",
                    base_url="https://openrouter.ai/api/v1",
                    api_key=config.openrouter_api_key,
                ),
                default_params=ModelParams(
                    temperature=0.1,
                    max_tokens=163840,
                ),
                capabilities=ModelCapabilities(
                    context_window=1024 * 163,
                    support_tools=True,
                    support_images=False,
                    support_structure_output=True,
                ),
            ),
            Model(
                id="openrouter-deepseek-r1",
                name="OpenRouter DeepSeek R1",
                description="deepseek-r1-0528:free",
                owner=SYSTEM_OWNER,
                provider=ProviderInfo(
                    model="deepseek/deepseek-r1-0528:free",
                    api_type="openai",
                    base_url="https://openrouter.ai/api/v1",
                    api_key=config.openrouter_api_key,
                ),
                default_params=ModelParams(
                    temperature=0.1,
                    max_tokens=163840,
                ),
                capabilities=ModelCapabilities(
                    context_window=1024 * 32,
                    support_tools=True,
                    support_images=False,
                    support_structure_output=True,
                ),
            ),
            Model(
                id="openrouter-qwen-qwen3-coder",
                name="OpenRouter Qwen Qwen 3 Coder",
                description="qwen-qwen3-coder:free",
                owner=SYSTEM_OWNER,
                provider=ProviderInfo(
                    model="qwen/qwen3-coder:free",
                    api_type="openai",
                    base_url="https://openrouter.ai/api/v1",
                    api_key=config.openrouter_api_key,
                ),
                default_params=ModelParams(
                    temperature=0.1,
                    max_tokens=262144,
                ),
                capabilities=ModelCapabilities(
                    context_window=1024 * 32,
                    support_tools=True,
                    support_images=False,
                    support_structure_output=True,
                ),
            ),
            Model(
                id="openrouter-qwen-qwen3-235b-a22b",
                name="OpenRouter Qwen 3 235B A22B",
                description="Qwen 3 35B A22B - 高质量中文MoE模型",
                owner=SYSTEM_OWNER,
                provider=ProviderInfo(
                    model="qwen/qwen3-235b-a22b:free",
                    api_type="openai",
                    base_url="https://openrouter.ai/api/v1",
                    api_key=config.openrouter_api_key,
                ),
                default_params=ModelParams(
                    temperature=0.1,
                    max_tokens=40960,
                ),
                capabilities=ModelCapabilities(
                    context_window=1024 * 32,
                    support_tools=True,
                    support_images=False,
                    support_structure_output=True,
                ),
            ),
            Model(
                id="openrouter-qwen-qwen3-30b-a3b",
                name="OpenRouter Qwen 3 30B A3B",
                description="Qwen 3 30B A3B - 高质量中文MoE模型",
                owner=SYSTEM_OWNER,
                provider=ProviderInfo(
                    model="qwen/qwen3-30b-a3b:free",
                    api_type="openai",
                    base_url="https://openrouter.ai/api/v1",
                    api_key=config.openrouter_api_key,
                ),
                default_params=ModelParams(
                    temperature=0.1,
                    max_tokens=40960,
                ),
                capabilities=ModelCapabilities(
                    context_window=1024 * 32,
                    support_tools=True,
                    support_images=False,
                    support_structure_output=True,
                ),
            ),
            Model(
                id="openrouter-moonshotai-kimi-k2",
                name="OpenRouter MoonshotAI Kimi K2",
                description="MoonshotAI Kimi K2",
                owner=SYSTEM_OWNER,
                provider=ProviderInfo(
                    model="moonshotai/kimi-k2:free",
                    api_type="openai",
                    base_url="https://openrouter.ai/api/v1",
                    api_key=config.openrouter_api_key,
                ),
                default_params=ModelParams(
                    temperature=0.1,
                    max_tokens=40960,
                ),
                capabilities=ModelCapabilities(
                    context_window=1024 * 32,
                    support_tools=True,
                    support_images=False,
                    support_structure_output=True,
                ),
            ),
            Model(
                id="openrouter-claude-3-5-sonnet",
                name="OpenRouter Claude 3.5 Sonnet",
                description="Claude 3.5 Sonnet - 高质量推理模型",
                owner=SYSTEM_OWNER,
                provider=ProviderInfo(
                    model="anthropic/claude-3.5-sonnet:free",
                    api_type="openai",
                    base_url="https://openrouter.ai/api/v1",
                    api_key=config.openrouter_api_key,
                ),
                default_params=ModelParams(
                    temperature=0.1,
                    max_tokens=4096,
                ),
                capabilities=ModelCapabilities(
                    context_window=1024 * 32,
                    support_tools=True,
                    support_images=False,
                    support_structure_output=True,
                ),
            ),
            Model(
                id="openrouter-openai-gpt-oss-20b",
                name="OpenRouter OpenAI GPT OSS 20B",
                description="GPT OSS 20B - OpenAI开源模型",
                owner=SYSTEM_OWNER,
                provider=ProviderInfo(
                    model="openai/gpt-oss-20b:free",
                    api_type="openai",
                    base_url="https://openrouter.ai/api/v1",
                    api_key=config.openrouter_api_key,
                ),
                default_params=ModelParams(
                    temperature=0.1,
                    max_tokens=131072,
                ),
                capabilities=ModelCapabilities(
                    context_window=1024 * 32,
                    support_tools=True,
                    support_images=False,
                    support_structure_output=True,
                ),
            ),
            Model(
                id="openrouter-z-ai-glm-4.5-air:free",
                name="OpenRouter 智谱 GLM 4.5 Air",
                description="Z AI GLM 4.5 Air - OpenRouter模型",
                owner=SYSTEM_OWNER,
                provider=ProviderInfo(
                    model="z-ai/glm-4.5-air:free",
                    api_type="openai",
                    base_url="https://openrouter.ai/api/v1",
                    api_key=config.openrouter_api_key,
                ),
                default_params=ModelParams(
                    temperature=0.1,
                    max_tokens=131072,
                ),
                capabilities=ModelCapabilities(
                    context_window=1024 * 32,
                    support_tools=True,
                    support_images=False,
                    support_structure_output=True,
                ),
            ),
            Model(
                id="deepseek-v3-chat",
                name="DeepSeek V3 Chat",
                description="DeepSeek V3 Chat - 官方DeepSeek API",
                owner=SYSTEM_OWNER,
                provider=ProviderInfo(
                    model="deepseek-chat",
                    api_type="openai",
                    base_url="https://api.deepseek.com/v1",
                    api_key=config.deepseek_api_key,
                ),
                default_params=ModelParams(
                    temperature=0.6,
                    max_tokens=65536,
                ),
                capabilities=ModelCapabilities(
                    context_window=1024 * 64,
                    support_tools=True,
                    support_images=False,
                    support_structure_output=True,
                ),
            ),
            Model(
                id="google-gemini-2.5-flash",
                name="Google Gemini 2.5 Flash",
                description="Google Gemini 2.5 Flash - 官方Google API",
                owner=SYSTEM_OWNER,
                provider=ProviderInfo(
                    model="models/gemini-2.5-flash",
                    api_type="google_genai",
                    api_key=config.gemini_api_key,
                ),
                default_params=ModelParams(
                    temperature=0.6,
                    max_tokens=65536,
                ),
                capabilities=ModelCapabilities(
                    context_window=1024 * 1024,
                    support_tools=True,
                    support_images=True,
                    support_structure_output=True,
                ),
            ),
            Model(
                id="google-gemini-2.5-flash-lite",
                name="Google Gemini 2.5 Flash Lite",
                description="Google Gemini 2.5 Flash Lite - 官方Google API",
                owner=SYSTEM_OWNER,
                provider=ProviderInfo(
                    model="models/gemini-2.5-flash-lite",
                    api_type="google_genai",
                    api_key=config.gemini_api_key,
                ),
                default_params=ModelParams(
                    temperature=0.6,
                    max_tokens=65536,
                ),
                capabilities=ModelCapabilities(
                    context_window=1024 * 1024,
                    support_tools=True,
                    support_images=True,
                    support_structure_output=True,
                ),
            ),
        ]
        from ..models.user import UserRole

        for m in default_models:
            await model_service.add_model(m, user_id=SYSTEM_OWNER, user_role=UserRole.ADMIN)
        logger.info("Default model data initialized via ModelService.")

    asyncio.run(_init_models())


def initialize_database() -> None:
    """Initialize database and create default data."""
    logger.info("Initializing database...")

    ensure_data_directory()
    create_default_admin_user()
    initialize_models_data()

    logger.info("Database initialization completed!")


if __name__ == "__main__":
    initialize_database()
