# Ensure the logs directory exists
import logging,os,inspect,sys,traceback


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
    Log an info message to the systems.log file.

    Args:
        message (str): The message to log.
    """
    try:
        frame = inspect.currentframe().f_back
        function_name = frame.f_code.co_name
        line_number = frame.f_lineno
        logger.info(f"{message} [Function: {function_name}, Line: {line_number}]")
    except Exception as e:
        print(f"Failed to log info: {e}")

def log_error(message: str, exc_info=None):
    """
    Log an error message with exception traceback if available.

    Args:
        message (str): The error message to log.
        exc_info: Exception information (optional). If None, will try to get current exception.
    """
    try:
        if exc_info is None:
            exc_info = sys.exc_info()
        
        if exc_info[0] is not None:  # If there's an active exception
            error_msg = f"{message}\n{''.join(traceback.format_exception(*exc_info))}"
        else:
            frame = inspect.currentframe().f_back
            function_name = frame.f_code.co_name
            line_number = frame.f_lineno
            error_msg = f"{message} [Function: {function_name}, Line: {line_number}]"
            
        logger.error(error_msg)
    except Exception as e:
        print(f"Failed to log error: {e}")