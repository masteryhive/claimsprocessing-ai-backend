
import asyncio,multiprocessing,time,uuid
from langchain_core.messages import HumanMessage
from src.error_trace.errorlogger import log_error
from src.ai.resources.document_understanding import classify_urls
from src.ai.claims_processing.run_workflow import  control_workflow
from src.ai.resources.db_ops import get_claim_from_database, update_claim_status_database
from src.database.schemas import Task, TaskStatus
from src.config.db_setup import SessionLocal
from src.datamodels.claim_processing import ClaimData, ProcessClaimTask
from src.distsys.rabbitmq import RabbitMQ
from src.ai.claims_processing.stirring_agent import super_graph
from src.utilities.helpers import _new_get_datetime

def process_message(body:bytes):
    """Process a single RabbitMQ message."""
    body_str = body.decode("utf-8") if isinstance(body, bytes) else body
    claim_request = ProcessClaimTask(
        claim_id=body_str,
        task_id=f"task_{str(uuid.uuid4())}",
    )
    print(f"Processing claim: {claim_request.model_dump()}")

    db = SessionLocal()
    try:
        # Create new task record
        existing_task = db.query(Task).filter_by(task_id=claim_request.task_id).first()
        if not existing_task:
            task = Task(
                task_id=claim_request.task_id, task_type="co_ai", status=TaskStatus.PENDING
            )
            db.add(task)
            db.commit()
            db.refresh(task)
        # Fetch claim data and stream processing
        claim_data = get_claim_from_database(claim_request.model_dump())
        claim_data['dateClaimFiled'] = _new_get_datetime(claim_data["createdAt"])
        if len(claim_data['resourceUrls']) != 0:
            loop = asyncio.get_event_loop()
            result = loop.run_until_complete(classify_urls(claim_data))
            claim_data.pop('resourceUrls', None)
            claim_data["evidenceProvided"] = result
        claim_data = ClaimData(**claim_data)
        
        print(claim_data)
        update_claim_status_database(claim_data.id,status=TaskStatus.PENDING)
        time.sleep(1)
        # Update task record
        task.status = TaskStatus.RUNNING
        db.commit()
        db.refresh(task)
        update_claim_status_database(claim_data.id,status=TaskStatus.RUNNING)
        team_summaries = {}
        for s in super_graph.stream(
            {
                "messages": [
                    HumanMessage(content=f"begin this claim processing:\n{claim_data}\n. YOU MUST USE THE SUMMARY TEAM TO PRESENT THE RESULT OF THIS TASK.")
                ]
            }
        ):
            if "__end__" not in s:
                control_workflow(db,claim_data.model_dump(),claim_data.id,claim_request,task,s,team_summaries)
                # Break the loop when 'summary_team' processes the claim
                if "summary_team" in s:
                    print("Summary team has completed processing. Exiting the loop.")
                    break
    except Exception as e:
        log_error(e)
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
