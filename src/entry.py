
from datetime import datetime, timezone
import multiprocessing
from langchain_core.messages import HumanMessage
from src.ai.resources.gen_mermaid import save_graph_mermaid
from src.ai.claims_processing.workflow_coordinator import run_coordinator
from src.ai.claims_processing.llm_flow import graph
from src.ai.resources.db_ops import get_claim_from_database, update_claim_status_database
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

        # Update task record
        task.status = TaskStatus.RUNNING
        db.commit()
        db.refresh(task)
        update_claim_status_database(claim_data["id"],status=TaskStatus.PENDING)
        save_graph_mermaid(graph)
        for s in graph.stream(
            {
                "messages": [
                    HumanMessage(content=f"begin this claim processing:\n{claim_data}")
                ]
            }
        ):
            if "__end__" not in s:
                run_coordinator(db,claim_data["id"],claim_request,task,s, s)
    finally:
        db.close()

if __name__ == "__main__":
    process_message("POL-2345-8764")
