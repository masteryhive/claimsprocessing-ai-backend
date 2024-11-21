import pika
import os

import logging

# Suppress pika logs below WARNING level
logging.getLogger("pika").setLevel(logging.WARNING)

# Optionally, suppress all logs below WARNING globally
logging.basicConfig(level=logging.WARNING)


class RabbitMQ:
    def __init__(self):
        self.user = os.getenv('RABBITMQ_USER', 'kbiueofd')
        self.password = os.getenv('RABBITMQ_PASSWORD', 'TMJ2ISGiU1nAbtMJQUK8WT0hLK5QrL4K')
        self.host = os.getenv('RABBITMQ_HOST', 'amqps://kbiueofd:TMJ2ISGiU1nAbtMJQUK8WT0hLK5QrL4K@sparrow.rmq.cloudamqp.com/kbiueofd')
        self.port = int(os.getenv('RABBITMQ_PORT', 5672))
        self.connection = None
        self.channel = None
        self.connect()

    def connect(self):
        credentials = pika.PlainCredentials(self.user, self.password)
        # parameters = pika.ConnectionParameters(host=self.host, port=self.port, credentials=credentials)
        parameters = pika.URLParameters(self.host)
        self.connection = pika.BlockingConnection(parameters)
        self.channel = self.connection.channel()

    def close(self):
        if self.connection and not self.connection.is_closed:
            self.connection.close()

    def consume(self, queue_name, callback):
        if not self.channel:
            raise Exception("Connection is not established.")
        self.channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
        self.channel.start_consuming()

    def publish(self, queue_name, message):
        if not self.channel:
            raise Exception("Connection is not established.")
        self.channel.queue_declare(queue=queue_name, durable=True)
        self.channel.basic_publish(exchange='',
                                   routing_key=queue_name,
                                   body=message,
                                   properties=pika.BasicProperties(
                                       delivery_mode=2,  # make message persistent
                                   ))
        # print(f"Sent message to queue {queue_name}: {message}")
