from fastapi import FastAPI, BackgroundTasks, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from datetime import datetime, timezone
import multiprocessing,uvicorn
from src.distsys.rabbitmq import RabbitMQ
from src.officer_interaction.llm_flow import graph
from langchain_core.messages import HumanMessage
from src.database.schemas import Task, TaskStatus
from src.officer_interaction.utilities.printer import fancy_print
from src.datamodels.co_ai import ProcessClaimTask
from src.config.db_setup import SessionLocal
from src.resources.db_ops import get_claim_from_database

app = FastAPI()


# Data model for input validation
class MessageRequest(BaseModel):
    message: str


def process_message(body):
    """Process a single RabbitMQ message."""
    body_str = body.decode("utf-8") if isinstance(body, bytes) else body
    claim_request = ProcessClaimTask(
        policy_number=body_str,
        task_id=f"task_{int(datetime.now(timezone.utc).timestamp())}",
    )
    print(f"Processing claim: {claim_request.model_dump()}")

    db = SessionLocal()
    try:
        # Create new task record
        task = Task(
            task_id=claim_request.task_id, task_type="co_ai", status=TaskStatus.PENDING
        )
        db.add(task)
        db.commit()
        db.refresh(task)

        # Fetch claim data and stream processing
        claim_data = get_claim_from_database(claim_request.model_dump())
        for s in graph.stream(
            {
                "messages": [
                    HumanMessage(content=f"begin this claim processing:\n{claim_data}")
                ]
            }
        ):
            if "__end__" not in s:
                fancy_print(s, s)
    finally:
        db.close()


def rabbitmq_worker():
    """Worker process to consume messages from RabbitMQ."""
    rabbitmq = RabbitMQ()
    while True:
        try:
            rabbitmq.consume(callback)
        except Exception as e:
            print(f"Error in RabbitMQ consumer: {e}")
            continue


def callback(ch, method, properties, body):
    """Callback function for RabbitMQ messages."""
    process = multiprocessing.Process(target=process_message, args=(body,))
    process.start()
    process.join()


@app.post("/start-worker",status_code=status.HTTP_202_ACCEPTED)
def start_worker(background_tasks: BackgroundTasks,):
    """HTTP endpoint to start the RabbitMQ worker."""
    try:
        background_tasks.add_task(rabbitmq_worker)
        return JSONResponse(
            status_code=status.HTTP_202_ACCEPTED,
            content={"status": "Worker started successfully"},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0")
