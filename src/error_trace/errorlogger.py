# Ensure the logs directory exists


def log_info(message: str):
    """
    Log an info message to the systems.log file.

    Args:
        message (str): The message to log.
    """
    try:
        print(message)
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
        print(message)
    except Exception as e:
        print(f"Failed to log error: {e}")