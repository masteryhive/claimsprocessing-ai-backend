import multiprocessing
from distsys.rabbitmq import RabbitMQ

def process_message(body):
    """Function to process a single message."""
    print(f"Processing {body}")

def callback(ch, method, properties, body):
    """Callback function invoked for each received message."""
    print(f"Received {body}")
    # Start a new process for each message
    process = multiprocessing.Process(target=process_message, args=(body,))
    process.start()
    # Optionally, join the process if you want to wait for it to complete
    process.join()

def main():
    """Main function to keep the consumer running."""
    rabbitmq = RabbitMQ()
    while True:  # Ensure the consumer is always running
        try:
            rabbitmq.consume("test", callback)
        except Exception as e:
            print(f"Error occurred: {e}")
            # Optionally, you can add logic here to restart the connection or handle specific errors
            continue

if __name__ == "__main__":
    main()
