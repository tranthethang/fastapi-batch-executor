"""
Logging configuration module for the application.
Sets up a unified logger that outputs to both the console and daily rotating files.
Logs are stored in the 'logs/' directory with a 'YYYYMMDD.log' naming convention.
"""

import logging
import os
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler

from pyflow_ai_stack.core.logger import logger


def setup_logger(logger_instance: logging.Logger):
    """
    Configure the provided logger instance with rotating file and console handlers.
    """
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    log_filename = os.path.join(log_dir, f"{datetime.now().strftime('%Y%m%d')}.log")

    logger_instance.setLevel(logging.INFO)

    if not logger_instance.handlers:
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

        # File Handler
        handler = TimedRotatingFileHandler(
            log_filename, when="midnight", interval=1, backupCount=30, encoding="utf-8"
        )
        handler.setFormatter(formatter)

        def namer(default_name):
            base_dir = os.path.dirname(default_name)
            parts = default_name.split(".")
            rotate_date_str = parts[-1]
            try:
                date_obj = datetime.strptime(rotate_date_str, "%Y-%m-%d")
                new_name = date_obj.strftime("%Y%m%d") + ".log"
            except ValueError:
                new_name = default_name
            return os.path.join(base_dir, new_name)

        handler.namer = namer
        logger_instance.addHandler(handler)

        # Console Handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger_instance.addHandler(console_handler)

    return logger_instance


# Configure and use the logger from pyflow-ai-stack
logger = setup_logger(logger)
