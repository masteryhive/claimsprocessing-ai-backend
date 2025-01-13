from contextlib import contextmanager
import time
import pika
import os
from error_trace.errorlogger import log_error
from config.appconfig import env_config
import logging

# Suppress pika logs below WARNING level
logging.getLogger("pika").setLevel(logging.WARNING)

# Optionally, suppress all logs below WARNING globally
logging.basicConfig(level=logging.WARNING)


class RobustRabbitMQConsumer:
    def __init__(
        self, 
        host: str = '34.44.208.42', 
        queue: str = env_config.amqp_queue, 
        max_retries: int = 5
    ):
        """
        Initialize RabbitMQ consumer with robust connection handling.
        
        Args:
            host (str): RabbitMQ server host
            queue (str): Queue to consume from
            max_retries (int): Maximum connection retry attempts
        """
        self.host = host
        self.queue = queue
        self.max_retries = max_retries
        self.connection = None
        self.channel = None
        
    @contextmanager
    def get_connection(self):
        """
        Context manager for RabbitMQ connection with exponential backoff.
        
        Yields:
            pika.adapters.blocking_connection.BlockingChannel: RabbitMQ channel
        """
        for attempt in range(self.max_retries):
            try:
                connection_params = pika.ConnectionParameters(
                    host=self.host,
                    connection_attempts=3,
                    retry_delay=1,
                    socket_timeout=5
                )
                
                self.connection = pika.BlockingConnection(connection_params)
                self.channel = self.connection.channel()
                
                # Declare queue to ensure it exists
                self.channel.queue_declare(
                    queue=self.queue, 
                    durable=True,  # Survive broker restart
                    exclusive=False
                )
                
                # Set prefetch count to distribute load
                self.channel.basic_qos(prefetch_count=1)
                
                yield self.channel
                break
            
            except (pika.exceptions.AMQPConnectionError, 
                    pika.exceptions.AMQPChannelError) as e:
                wait_time = 2 ** attempt  # Exponential backoff
                log_error(f"RabbitMQ connection attempt {attempt + 1} failed: {e}")
                
                if attempt == self.max_retries - 1:
                    log_error("Max connection attempts reached. Exiting.")
                    raise
                
                time.sleep(wait_time)
            finally:
                if self.connection and not self.connection.is_closed:
                    self.connection.close()

