import concurrent.futures

class AgentToolExecutor:
    def __init__(self, max_workers: int = 3):
        """
        Initialize the tool executor with a thread pool.
        
        Args:
            max_workers (int): Maximum number of concurrent workers/threads
        """
        self.executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=max_workers
        )
    
    def execute_non_blocking(self, func, *args, **kwargs):
        """
        Execute a function non-blockingly and return immediately.
        
        Args:
            func (Callable): Function to execute
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function
        
        Returns:
            concurrent.futures.Future: Future representing the function's execution
        """
        try:
            future = self.executor.submit(func, *args, **kwargs)
            return future
        except Exception as e:
            print(f"Error executing non-blocking task: {e}")
            raise

# Global executor instance
agent_tool_executor = AgentToolExecutor()