# Ensure the logs directory exists
import inspect
import logging
import os


LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "systems.log")
os.makedirs(LOG_DIR, exist_ok=True)

# Configure logging
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Logger instance
logger = logging.getLogger("production_logger")

def log_info(message: str):
    """
    Log an error message to the systems.log file.

    Args:
        message (str): The error message to log.
    """
    try:
        # Capture the current function and line number
        frame = inspect.currentframe().f_back
        function_name = frame.f_code.co_name
        line_number = frame.f_lineno
        logger.info(f"{message} [Function: {function_name}, Line: {line_number}]")
    except Exception as e:
        # Fallback if logging fails
        print(f"Failed to log error: {e}")

def log_error(message: str):
    """
    Log an error message to the systems.log file.

    Args:
        message (str): The error message to log.
    """
    try:
        # Capture the current function and line number
        frame = inspect.currentframe().f_back
        function_name = frame.f_code.co_name
        line_number = frame.f_lineno
        logger.error(f"{message} [Function: {function_name}, Line: {line_number}]")
    except Exception as e:
        # Fallback if logging fails
        print(f"Failed to log error: {e}")