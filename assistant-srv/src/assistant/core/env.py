import logging
import logging.config
import os
from typing import Any, Dict, List

import yaml
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


class Env:
    env: str = ""
    env_file_suffix: str = ""
    log_config: Dict[str, Any] = {}
    files_loaded: List[str] = []

    @staticmethod
    def init() -> None:
        Env.env = os.getenv("ENV", "")
        Env.env_file_suffix = f".{Env.env}" if Env.env else ""
        env_file = f".env{Env.env_file_suffix}"
        load_dotenv(dotenv_path=env_file)
        load_dotenv(dotenv_path=f"{env_file}.local")  # 支持 .env.local 叠加
        Env.files_loaded.append(os.path.abspath(env_file))
        Env.files_loaded.append(os.path.abspath(f"{env_file}.local"))
        Env.log_config = Env._get_log_config()
        logging.config.dictConfig(Env.log_config)

        for file in Env.files_loaded:
            logger.info(f"Loaded configuration file: {file}")

    @staticmethod
    def get_env() -> str:
        return Env.env

    @staticmethod
    def get_env_file_suffix() -> str:
        return Env.env_file_suffix

    @staticmethod
    def get_log_config() -> Dict[str, Any]:
        return Env.log_config

    @staticmethod
    def _get_log_config() -> Dict[str, Any]:
        """Load logging configuration from YAML file."""
        log_config_file = os.getenv("LOG_CONFIG_FILE", f"logging{Env.env_file_suffix}.yaml")
        Env.files_loaded.append(os.path.abspath(log_config_file))
        with open(log_config_file, "r") as f:
            log_config = yaml.safe_load(f)
            if not isinstance(log_config, dict):
                raise ValueError(f"Invalid logging configuration in {log_config_file}: Expected a dictionary.")

        return log_config
