import json, asyncio, uuid
from typing import Any, Dict
from rag.context_stuffing import delete_pdf
from utilities.helpers import _new_get_datetime

from database.schemas import Task, TaskStatus
from config.db_setup import SessionLocal
from models.claim_processing import (
    AccidentClaimData,
    ProcessClaimTask,
    TheftClaimData,
)
from database.db_ops import (
    get_claim_from_database,
    update_claim_status_database,
)

from langchain_core.messages import HumanMessage
# # from error_trace.errorlogger import log_error, log_info
from teams.resources.document_understanding import classify_supporting_documents
from run_workflow import control_workflow

# from distsys.rabbitmq import RobustRabbitMQConsumer
from stirring_agent import super_graph



def process_message(id: int):
    """
    Robust message processing with comprehensive error handling.

    Args:
        id (int): Claim ID to process
    """
    claim_request = ProcessClaimTask(
        claim_id=id, task_id=f"task_{str(uuid.uuid4())}"
    )
    db = SessionLocal()
    try:
        # Comprehensive task and claim data management
        existing_task = db.query(Task).filter_by(claim_id=claim_request.claim_id).first()
        if existing_task:
            task = existing_task
        else:
            task = Task(
                task_id=claim_request.task_id,
                claim_id=claim_request.claim_id,
                task_type="co_ai",
                status=TaskStatus.PENDING,
            )
            db.add(task)
            db.commit()
            db.refresh(task)

        # Fetch and process claim data
        claim_data = get_claim_from_database(task.claim_id)
        claim_data["dateClaimFiled"] = _new_get_datetime(claim_data["createdAt"])

        # Process URLs if present
        if claim_data.get("resourceUrls"):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(classify_supporting_documents(claim_data))
                claim_data = result
            finally:
                loop.close()
        claim_id = claim_data["id"]
        # Type-specific claim data processing
        claim_data = (
            AccidentClaimData(**claim_data)
            if claim_data["claimType"] in ["Accident", "accident"]
            else TheftClaimData(**claim_data)
        )

        # Update claim and task statuses
        update_claim_status_database(claim_id, status=TaskStatus.PENDING)

        task.status = TaskStatus.RUNNING
        db.commit()
        db.refresh(task)

        update_claim_status_database(claim_id, status=TaskStatus.RUNNING)

        # Process claim workflow
        team_summaries: Dict[str, Any] = {}
        for s in super_graph.stream(
            {
                "messages": [
                    HumanMessage(
                        content=(
                            "Important information:"
                            "\nThis service is currently run in Nigeria, this means:"
                            "\n1. The currency is \u20a6"
                            f"\n\nBegin this claim processing using this claim form JSON data:\n {claim_data.model_dump()}"
                            "\n\nYOU MUST USE THE SUMMARY TEAM TO PRESENT THE RESULT OF THIS TASK."
                        )
                    )
                ],
                "claim_form_json":[HumanMessage(
                        content=json.dumps(claim_data.model_dump()))]
            }
        ):
            if "__end__" not in s:
                control_workflow(
                    db,
                    claim_data.model_dump(),
                    claim_id,
                    claim_request,
                    task,
                    s,
                    team_summaries,
                )

                if "summary_team" in s:
                    # log_info("Summary team has completed processing.")
                    break
        delete_pdf(claim_data['policyNumber'])
    except Exception as e:
        print(e)
        # log_error(f"Claim processing error: {e}", sys.exc_info())
        # Consider adding logic to handle unprocessable messages

    finally:
        db.close()


# def rabbitmq_worker():
#     """
#     Enhanced RabbitMQ worker with robust connection and consumption management.
#     """
#     consumer = RobustRabbitMQConsumer()

#     while True:
#         try:
#             with consumer.get_connection() as channel:

#                 def safe_callback(ch, method, properties, body):
#                     try:
#                         process = multiprocessing.Process(
#                             target=process_message, args=(body,)
#                         )
#                         process.start()
#                         process.join(timeout=300)  # 5-minute timeout

#                         if process.is_alive():
#                             process.terminate()
#                             log_error("Process exceeded time limit and was terminated")
#                             # Potentially requeue the message
#                             ch.basic_nack(
#                                 delivery_tag=method.delivery_tag, requeue=True
#                             )
#                         else:
#                             # Acknowledge message only if processing completes successfully
#                             ch.basic_ack(delivery_tag=method.delivery_tag)

#                     except Exception as e:
#                         log_error(f"Callback processing error: {e}")
#                         # Negative acknowledge and requeue
#                         ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

#                 channel.basic_consume(
#                     queue=consumer.queue, on_message_callback=safe_callback
#                 )

#                 log_error("RabbitMQ consumer started. Waiting for messages...")
#                 channel.start_consuming()

#         except Exception as e:
#             log_error(f"RabbitMQ worker error: {e}")
#             time.sleep(10)  # Wait before retry to prevent tight error loops


# def callback(ch, method, properties, body):
#     """Callback function for RabbitMQ messages."""
#     process = multiprocessing.Process(target=process_message, args=(body,))
#     process.start()
#     process.join()

