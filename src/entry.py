import datetime
import json
import multiprocessing
from distsys.rabbitmq import RabbitMQ
from officer_interaction.llm_flow import graph
from langchain_core.messages import HumanMessage
from database.schemas import Task,TaskStatus
from officer_interaction.utilities.printer import fancy_print
from datamodels.co_ai import ProcessClaimTask
from src.config.db_setup import SessionLocal
from sqlalchemy.orm import Session

def process_message(body):
    """Function to process a single message."""
    print(f"Processing {body}")
    body_str = body.decode('utf-8')
    claim_request = ProcessClaimTask(policy_number=body_str,task_id=f"task_{int(datetime.utcnow().timestamp())}")
    print(claim_request.model_dump())
    db = SessionLocal()
    # Create new task record
    task = Task(
        task_id=claim_request.task_id,
        task_type="co_ai",
        status=TaskStatus.PENDING
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    db.close()
    for s in graph.stream({"messages": [HumanMessage(content=f"begin this claim processing:\n{claim_request.model_dump()}")]}):
        if "__end__" not in s:
            #print(s)
            fancy_print(s,s)

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
