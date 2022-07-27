import logging
import sys

from logging.handlers import RotatingFileHandler

from agent.config_provider import config_provider


# todo should I create separate logger in every file? I can pass name... it it will appear in logs
def get_logger(name, level=None, stdout=True) -> logging.Logger:
    logger_ = logging.getLogger(name)
    if level:
        logger_.setLevel(level)

    file_handler = RotatingFileHandler(
        config_provider['log_file_path'],
        maxBytes=config_provider.get('log_file_max_size_bytes', 10000000),
        backupCount=config_provider.get('log_file_backup_count', 5),
    )
    # file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger_.addHandler(file_handler)

    if stdout:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.INFO)
        handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logger_.addHandler(handler)

    return logger_


logger = get_logger(
    __name__, config_provider.get('log_level', logging.INFO), stdout=config_provider.get('log_to_stdout', False)
)
