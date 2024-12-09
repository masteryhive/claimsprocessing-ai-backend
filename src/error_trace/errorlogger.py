# Ensure the logs directory exists
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


def log_error(message: str):
    """
    Log an error message to the systems.log file.

    Args:
        message (str): The error message to log.
    """
    try:
        logger.error(message)
    except Exception as e:
        # Fallback if logging fails
        print(f"Failed to log error: {e}")