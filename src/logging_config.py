# logging_config.py
import logging
from logging.handlers import RotatingFileHandler


# Centralized logger setup
def setup_logger():
    logger = logging.getLogger("dao_voting_agent")  # Using the same logger name across all files (centralized logging)
    logger.setLevel(logging.INFO)  # Set log level to INFO (or maybe to DEBUG if there'll be any need for that)

    # This is in order to avoid adding duplicate handlers if setup_logger is called multiple times
    if not logger.handlers:
        # Rotating file handler (10MB file, 7 backups): Every 7th log-file will auto delete once there's a new one)
        log_file = "dao_voting_agent.log"
        file_handler = RotatingFileHandler(log_file, maxBytes=10 * 1024 * 1024, backupCount=7)
        file_handler.setLevel(logging.INFO)

        # Format for the file handler
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)

        # Add only the file handler to the logger (The system will only write to log the file, no printing into console)
        logger.addHandler(file_handler)

    return logger
