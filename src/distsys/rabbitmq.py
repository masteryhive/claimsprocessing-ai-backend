import pika
import os
from src.config.appconfig import env_config
import logging

# Suppress pika logs below WARNING level
logging.getLogger("pika").setLevel(logging.WARNING)

# Optionally, suppress all logs below WARNING globally
logging.basicConfig(level=logging.WARNING)


class RabbitMQ:
    def __init__(self):
        self.connection = None
        self.channel = None
        self.connect()

    def connect(self):
        # parameters = pika.ConnectionParameters(host=self.host, port=self.port, credentials=credentials)
        parameters = pika.URLParameters(env_config.amqp)
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='104.154.137.57'))
        self.channel = self.connection.channel()

    def close(self):
        if self.connection and not self.connection.is_closed:
            self.connection.close()

    def consume(self,  callback, queue_name="claims_processing"):
        if not self.channel:
            raise Exception("Connection is not established.")
        self.channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
        self.channel.start_consuming()

