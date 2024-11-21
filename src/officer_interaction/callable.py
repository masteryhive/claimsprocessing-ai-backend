import json
from sqlalchemy.orm import Session
from src.services.ai.resources.db_ops import get_claim_from_database
from src.config.db_setup import SessionLocal
from src.database.schemas import Task, TaskStatus
from src.datamodels.co_ai import ProcessClaimTask
from datetime import datetime, timezone
from langchain_core.messages import HumanMessage,AIMessage
import logging
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def call_agent_starter(policy_dict:dict):
    print("here >>> ",policy_dict)
    claim_request = ProcessClaimTask
    claim_request.policy_number = policy_dict["policy_number"]
    claim_request.task_id = f"task_{int(datetime.now(timezone.utc).timestamp())}"
    print("claim_request >>> ",claim_request)
    try:
        db = next(get_db())
        # Create new task record
        task = Task(
        task_id=claim_request.task_id,
        task_type="co_ai",
        status=TaskStatus.PENDING
        )
        db.add(task)
        db.commit()
        db.refresh(task)
    except Exception as e:
        print(e)

    stirring_agent_tasks(claim_request,db)


def stirring_agent_tasks(claim_task: ProcessClaimTask,db: Session):
    """Simulate a long running process"""
    # Update task status to running
    task = (db.query(Task)
    .filter(Task.task_id == claim_task.task_id)
    .first()
    )
    task.status = TaskStatus.RUNNING
    task.started_at = datetime.now(timezone.utc)
    db.commit()
    
    try:
        data = get_claim_from_database(claim_task.policy_number)
        # # save_graph_mermaid(ofg, 'my_langgraph.png')
        initial_state = {"messages": [HumanMessage(content=f"begin this claim processing:\n{json.dumps(data)}" )]}
        thread = {"configurable": {"thread_id": ""}}
        # for s in ofg.stream(initial_state, thread):
        #     fancy_print(s,s)
        import time

        # Set a 15-second delay
        time.sleep(15)

        # Update task as completed
        task.status = TaskStatus.COMPLETED
        task.completed_at = datetime.now(timezone.utc)
        task.result = "Task completed successfully"
        db.commit()
        
    except Exception as e:
        logger.error(f"Task {claim_task.policy_id} failed: {e}")