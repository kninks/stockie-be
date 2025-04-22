import logging
import os
from typing import Optional

from app.core.enums.roles_enum import RoleEnum

logger = logging.getLogger(__name__)


class Config:
    def __init__(self):
        from dotenv import load_dotenv

        if os.getenv("ENVIRONMENT", "local") == "local":
            load_dotenv()

        self.ENVIRONMENT = self._require_env("ENVIRONMENT")

        self.DATABASE_URL = self._require_env("DATABASE_URL")
        self.ML_SERVER_URL = self._require_env("ML_SERVER_URL")
        self.DISCORD_WEBHOOK_URL = self._require_env("DISCORD_WEBHOOK_URL")

        self.REDIS_HOST = self._optional_env("REDIS_HOST", "localhost")
        self.REDIS_PORT = int(self._optional_env("REDIS_PORT", "6379"))
        self.REDIS_DB = int(self._optional_env("REDIS_DB", "0"))

        self.CLIENT_API_KEY = self._require_env("CLIENT_API_KEY")
        self.BACKEND_API_KEY = self._require_env("BACKEND_API_KEY")
        self.ML_SERVER_API_KEY = self._require_env("ML_SERVER_API_KEY")
        self.ALLOWED_API_KEYS = {
            RoleEnum.CLIENT: self.CLIENT_API_KEY,
            RoleEnum.BACKEND: self.BACKEND_API_KEY,
            RoleEnum.ML_SERVER: self.ML_SERVER_API_KEY,
        }

        self.DEBUG = os.getenv("DEBUG", "False").lower() == "true"

        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
        if self.LOG_LEVEL not in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}:
            logger.warning("Invalid LOG_LEVEL, defaulting to INFO")
            raise ValueError(
                "Invalid LOG_LEVEL, must be one of: DEBUG, INFO, WARNING, ERROR, CRITICAL"
            )

        # allowed_origins = os.getenv("ALLOWED_ORIGINS", "https://stockie-fe.vercel.app/")
        allowed_origins = "https://stockie-fe.vercel.app,https://stockie-ml-996128501833.asia-southeast1.run.app,http://localhost:5173,http://127.0.0.1:5173,http://localhost:8000,http://127.0.0.1:8000,http://localhost:8001,http://127.0.0.1:8001"
        self.ALLOWED_ORIGINS = [origin.strip() for origin in allowed_origins.split(",")]

    @staticmethod
    def _require_env(var_name: str, default_value: Optional[str] = None) -> str:
        value = os.getenv(var_name, default_value)
        if not value:
            logger.critical(f"Missing required environment variable: {var_name}")
            raise ValueError(f"Missing environment variable: {var_name}")
        return value

    @staticmethod
    def _optional_env(var_name: str, default_value: str) -> str:
        value = os.getenv(var_name, default_value)
        if not value:
            logger.warning(
                f"Missing optional environment variable: {var_name}, using default: {default_value}"
            )
        return value


_config = None


def get_config():
    global _config
    if _config is None:
        _config = Config()
    return _config
