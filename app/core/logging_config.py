import os
import logging
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime

def setup_logging():
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Base logger configuration
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Clean up existing handlers to avoid duplicates
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File Handler with Daily Rotation
    # Use current date for the active log file
    current_date = datetime.now().strftime("%Y%m%d")
    log_file = os.path.join(log_dir, f"{current_date}.log")
    
    file_handler = TimedRotatingFileHandler(
        log_file,
        when="midnight",
        interval=1,
        backupCount=30,
        encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    
    # Custom namer to ensure rotated files follow the same pattern
    def namer(default_name):
        # default_name is like 20260201.log.2026-02-02
        base_dir = os.path.dirname(default_name)
        # Extract the date part that TimedRotatingFileHandler appends
        parts = default_name.split('.')
        # The rotation date is usually the last part
        rotate_date_str = parts[-1] 
        try:
            # The date in default_name for midnight rotation is the date of the log *before* rotation
            date_obj = datetime.strptime(rotate_date_str, "%Y-%m-%d")
            new_name = date_obj.strftime("%Y%m%d") + ".log"
        except ValueError:
            new_name = default_name
            
        return os.path.join(base_dir, new_name)

    file_handler.namer = namer
    logger.addHandler(file_handler)
    
    # Optional: silence some noisy loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

