import logging
import os

from dotenv import load_dotenv

from app.core.enums.roles_enum import RoleEnum

load_dotenv()

logger = logging.getLogger(__name__)


class Config:
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        logger.critical("Missing DATABASE_URL environment variable")
        raise ValueError("Missing DATABASE_URL environment variable")

    ML_SERVER_URL = os.getenv("ML_SERVER_URL")
    if not ML_SERVER_URL:
        logger.critical("Missing ML_SERVER_URL environment variable")
        raise ValueError("Missing ML_SERVER_URL environment variable")

    SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key_for_local_dev")
    if not SECRET_KEY:
        logger.warning("Missing SECRET_KEY environment variable")
        raise ValueError("Missing SECRET_KEY environment variable")

    CLIENT_API_KEY = os.getenv("CLIENT_API_KEY")
    if not CLIENT_API_KEY:
        logger.warning("Missing CLIENT_API_KEY environment variable")
        raise ValueError("Missing CLIENT_API_KEY environment variable")

    BACKEND_API_KEY = os.getenv("BACKEND_API_KEY")
    if not BACKEND_API_KEY:
        logger.warning("Missing BACKEND_API_KEY environment variable")
        raise ValueError("Missing BACKEND_API_KEY environment variable")

    ML_SERVER_API_KEY = os.getenv("ML_SERVER_API_KEY")
    if not ML_SERVER_API_KEY:
        logger.warning("Missing ML_SERVER_API_KEY environment variable")
        raise ValueError("Missing ML_SERVER_API_KEY environment variable")

    DEBUG = os.getenv("DEBUG", "False").lower() == "true"

    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    if LOG_LEVEL not in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}:
        logger.warning("Invalid LOG_LEVEL, defaulting to INFO")
        raise ValueError(
            "Invalid LOG_LEVEL, must be one of: DEBUG, INFO, WARNING, ERROR, CRITICAL"
        )

    ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*")
    ALLOWED_ORIGINS = ALLOWED_ORIGINS.split(",") if ALLOWED_ORIGINS else ["*"]

    ALLOWED_API_KEYS = {
        RoleEnum.CLIENT: CLIENT_API_KEY,
        RoleEnum.BACKEND: BACKEND_API_KEY,
        RoleEnum.ML_SERVER: ML_SERVER_API_KEY,
    }


config = Config()
