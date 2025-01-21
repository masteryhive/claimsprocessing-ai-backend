from src.error_trace.errorlogger import system_logger
from functools import wraps

def async_retry_decorator(max_attempts: int = 3, base_wait: float = 1):
    """
    Decorator for async functions that implements exponential backoff retry logic
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        system_logger.error(
                            error=f"Final retry attempt failed for {func.__name__}: {str(e)}"
                        )
                        raise
                    wait_time = base_wait * (2**attempt)
                    system_logger.warning(
                        message=f"Attempt {attempt + 1} failed for {func.__name__}: {str(e)}. Retrying in {wait_time}s"
                    )
                    await asyncio.sleep(wait_time)

        return wrapper

    return decorator
