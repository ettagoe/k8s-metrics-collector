import logging
import sys

from logging.handlers import RotatingFileHandler

from src.agent.config_provider import config_provider


# todo level
def get_logger(name, level=None, stdout=False) -> logging.Logger:
    logger = logging.getLogger(name)
    if level:
        logger.setLevel(level)

    # todo it used to have 'agent.log', you might need to bring it back if logs are not working
    file_handler = RotatingFileHandler(
        config_provider['log_file_path'],
        maxBytes=config_provider.get('log_file_max_size_bytes', 5000),
        backupCount=config_provider.get('log_file_backup_count', 5),
    )
    # file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(file_handler)

    if stdout:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.INFO)
        handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logger.addHandler(handler)

    return logger
