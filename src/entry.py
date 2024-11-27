
from datetime import datetime, timezone
import multiprocessing
from langchain_core.messages import HumanMessage
from src.ai.claims_processing.utilities.printer import fancy_print
from src.ai.claims_processing.llm_flow import graph
from src.ai.resources.db_ops import get_claim_from_database
from src.database.schemas import Task, TaskStatus
from src.config.db_setup import SessionLocal
from src.datamodels.co_ai import ProcessClaimTask
from src.distsys.rabbitmq import RabbitMQ


def process_message(body:str):
    """Process a single RabbitMQ message."""
    claim_request = ProcessClaimTask(
        policy_number=body,
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

        # Create new task record
        task = Task(
            task_id=claim_request.task_id, task_type="co_ai", status=TaskStatus.RUNNING
        )
        db.add(task)
        db.commit()
        db.refresh(task)

        for s in graph.stream(
            {
                "messages": [
                    HumanMessage(content=f"begin this claim processing:\n{claim_data}")
                ]
            }
        ):
            if "__end__" not in s:
                fancy_print(claim_request,s, s)
    finally:
        db.close()

if __name__ == "__main__":
    process_message()
