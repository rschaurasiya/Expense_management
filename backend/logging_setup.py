import os
import logging

def setup_Logger(name, log_file="server_check.log", level=logging.DEBUG):
    # Create a custom logger
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.handlers:
        backend_dir = os.path.dirname(os.path.abspath(__file__))
        log_path = os.path.join(backend_dir, log_file)
        file_handler = logging.FileHandler(log_path)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger