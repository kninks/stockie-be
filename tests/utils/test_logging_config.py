# import logging
# import os
# import json
# import pytest
# from app.utils.logging_config import setup_logging
#
# @pytest.fixture(autouse=True)
# def configure_logging():
#     """Ensure logging is set up before each test."""
#     setup_logging()
#
# def test_logging_initialization():
#     """Test if logging is initialized correctly."""
#     logger = logging.getLogger("test_logger")
#     assert logger is not None
#
# def test_logging_levels():
#     """Test that log levels work as expected."""
#     logger = logging.getLogger("test_logger")
#     assert logger.isEnabledFor(logging.DEBUG)
#     assert logger.isEnabledFor(logging.INFO)
#     assert logger.isEnabledFor(logging.WARNING)
#     assert logger.isEnabledFor(logging.ERROR)
#     assert logger.isEnabledFor(logging.CRITICAL)
#
# def test_log_to_file():
#     """Ensure logs are written to the file."""
#     log_file = "logs/app.log"
#     logger = logging.getLogger("test_logger")
#
#     logger.info("Test log entry")
#
#     with open(log_file, "r") as file:
#         log_content = file.read()
#         assert "Test log entry" in log_content
#
# def test_json_log_format():
#     """Verify JSON log format is correct."""
#     json_log_file = "logs/forwarder.log"
#     logger = logging.getLogger("test_logger")
#
#     logger.info("JSON log test")
#
#     with open(json_log_file, "r") as file:
#         log_entry = file.readlines()[-1]  # Get last log entry
#         log_data = json.loads(log_entry)
#
#         assert "time" in log_data
#         assert "logger" in log_data
#         assert "level" in log_data
#         assert "message" in log_data
#         assert log_data["message"] == "JSON log test"
#
# def test_debug_logging_enabled(monkeypatch):
#     """Check if debug mode enables DEBUG level logging."""
#     monkeypatch.setattr("app.config.config.DEBUG", True)  # Force DEBUG mode
#     setup_logging()
#
#     logger = logging.getLogger("test_logger")
#     assert logger.isEnabledFor(logging.DEBUG)
#
# def test_debug_logging_disabled(monkeypatch):
#     """Check if disabling debug mode sets logging to INFO level."""
#     monkeypatch.setattr("app.config.config.DEBUG", False)  # Force INFO mode
#     setup_logging()
#
#     logger = logging.getLogger("test_logger")
#     assert not logger.isEnabledFor(logging.DEBUG)  # DEBUG should be OFF
