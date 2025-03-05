import os
import sys
import json
from logging.config import dictConfig

from colorlog import ColoredFormatter

COMMON_DATEFMT = "%Y-%m-%d %H:%M:%S"

def setup_logging():
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s [%(levelname)s] %(name)s - %(message)s",
                "datefmt": COMMON_DATEFMT,
            },
            "colored": {
                "()": ColoredFormatter,
                "format": "%(asctime)s %(log_color)s[%(levelname)s]%(reset)s %(name_log_color)s%(name)s%(reset)s - %(message)s",
                "datefmt": COMMON_DATEFMT,
                "log_colors": {
                    "DEBUG":    "cyan",
                    "INFO":     "green",
                    "WARNING":  "yellow",
                    "ERROR":    "red",
                    "CRITICAL": "white,bg_red",
                },
                "secondary_log_colors": {
                    "name": {
                        "DEBUG": "light_blue",
                        "INFO": "blue",
                        "WARNING": "magenta",
                        "ERROR": "purple",
                        "CRITICAL": "red",
                    },
                },
            },
            "json": {
                # For JSON, you can reuse the same date format
                "format": json.dumps({
                    "time": "%(asctime)s",
                    "logger": "%(name)s",
                    "level": "%(levelname)s",
                    "message": "%(message)s"
                }),
                "datefmt": COMMON_DATEFMT,
            },
        },

        # Handlers send log records to various outputs (like console or files).
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "stream": sys.stdout,
                "formatter": "colored",
                "level": "INFO",
            },
            "file": {
                "class": "logging.FileHandler",
                "filename": os.path.join(log_dir, "app.log"),
                "formatter": "default",  # Human-readable file logs
                "level": "INFO",
            },
            "forwarder": {
                "class": "logging.FileHandler",
                "filename": os.path.join(log_dir, "forwarder.log"),
                "formatter": "json",  # JSON-formatted logs for external forwarding
                "level": "INFO",
            },
        },

        "root": {
            "handlers": ["console", "file", "forwarder"],
            "level": "INFO",
        },
    }
    dictConfig(config)