import logging
import sys
import os

def setup_logger(name=__name__, log_level=logging.INFO):
    """
    Configures and returns a logger with standard formatting.
    """
    logger = logging.getLogger(name)
    
    # Prevent duplicate handlers if multiple imports
    if logger.handlers:
        return logger
        
    logger.setLevel(log_level)
    
    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    
    # Formatting
    formatter = logging.Formatter(
        '%(asctime)s - [%(levelname)s] - %(name)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    
    logger.addHandler(console_handler)
    
    # File Handler (Optional)
    # Ensure logs directory exists
    log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
    os.makedirs(log_dir, exist_ok=True)
    
    file_path = os.path.join(log_dir, "app.log")
    file_handler = logging.FileHandler(file_path)
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger
