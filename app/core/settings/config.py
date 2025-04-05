import logging
import os

from dotenv import load_dotenv

from app.core.enums.roles_enum import RoleEnum

load_dotenv()

logger = logging.getLogger(__name__)


class Config:
    def __init__(self):
        self.DATABASE_URL = os.getenv("DATABASE_URL")
        if not self.DATABASE_URL:
            logger.critical("Missing DATABASE_URL environment variable")
            raise ValueError("Missing DATABASE_URL environment variable")

        self.ML_SERVER_URL = os.getenv("ML_SERVER_URL")
        if not self.ML_SERVER_URL:
            logger.critical("Missing ML_SERVER_URL environment variable")
            raise ValueError("Missing ML_SERVER_URL environment variable")

        # self.SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key_for_local_dev")
        # if not self.SECRET_KEY:
        #     self.logger.warning("Missing SECRET_KEY environment variable")
        #     raise ValueError("Missing SECRET_KEY environment variable")

        self.CLIENT_API_KEY = os.getenv("CLIENT_API_KEY")
        self.BACKEND_API_KEY = os.getenv("BACKEND_API_KEY")
        self.ML_SERVER_API_KEY = os.getenv("ML_SERVER_API_KEY")

        for key_name, key_value in {
            "CLIENT_API_KEY": self.CLIENT_API_KEY,
            "BACKEND_API_KEY": self.BACKEND_API_KEY,
            "ML_SERVER_API_KEY": self.ML_SERVER_API_KEY,
        }.items():
            if not key_value:
                logger.warning(f"Missing {key_name} environment variable")
                raise ValueError(f"Missing {key_name} environment variable")

        self.DEBUG = os.getenv("DEBUG", "False").lower() == "true"

        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
        if self.LOG_LEVEL not in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}:
            logger.warning("Invalid LOG_LEVEL, defaulting to INFO")
            raise ValueError(
                "Invalid LOG_LEVEL, must be one of: DEBUG, INFO, WARNING, ERROR, CRITICAL"
            )

        allowed_origins = os.getenv("ALLOWED_ORIGINS", "*")
        self.ALLOWED_ORIGINS = allowed_origins.split(",") if allowed_origins else ["*"]

        self.ALLOWED_API_KEYS = {
            RoleEnum.CLIENT: self.CLIENT_API_KEY,
            RoleEnum.BACKEND: self.BACKEND_API_KEY,
            RoleEnum.ML_SERVER: self.ML_SERVER_API_KEY,
        }


config = Config()
