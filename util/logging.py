import logging
import sys

def setup_logging():
    """
    Set up logging configuration for the entire application.
    Configures both console and file handlers with a detailed formatter.
    """
    # Create formatter that includes timestamp, level, logger name, function, and message
    formatter = logging.Formatter(
        fmt='%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Create console handler and set formatter
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)  # Set console to INFO level

    # Create file handler for persistent logs
    file_handler = logging.FileHandler('bot.log')
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)  # Set file handler to DEBUG level

    # Get the root logger and configure handlers
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)  # Set root logger to DEBUG to capture all levels
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

def get_logger(module_name):
    """
    Get a logger specific to the provided module name.
    Ensures that logs are clearly tagged with the module's name.
    
    :param module_name: The name of the module requesting the logger.
    :return: A configured logger for the module.
    """
    return logging.getLogger(module_name)