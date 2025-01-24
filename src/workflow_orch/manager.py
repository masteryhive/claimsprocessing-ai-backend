from pathlib import Path
import json, asyncio, uuid
from src.utilities.pdf_handlers import delete_pdf
from src.utilities.helpers import _new_get_datetime
from src.error_trace.errorlogger import system_logger
from src.database.schemas import Task, TaskStatus
from src.config.db_setup import SessionLocal
from sqlalchemy.orm import sessionmaker
from src.models.claim_processing import (
    AccidentClaimData,
    ProcessClaimTask,
    TheftClaimData,
)
from src.database.db_ops import (
    get_claim_from_database,
    update_claim_status_database,
)
from src.models.claim_processing import UpdateClaimsReportModel
from tenacity import retry, stop_after_attempt, wait_exponential
from langchain_core.messages import HumanMessage
from src.teams.resources.document_understanding import classify_supporting_documents
from src.workflow_orch.run_workflow import control_workflow
from contextlib import contextmanager
from src.teams.stirring_agent import super_graph
from sqlalchemy.exc import SQLAlchemyError

rag_path = Path(__file__).parent / "teams/policy_doc/"

class ClaimProcessingError(Exception):
    """Custom exception for claim processing errors."""
    pass

@contextmanager
def database_session():
    """Context manager for database sessions with proper error handling."""
    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError as e:
        db.rollback()
        system_logger.error(f"Database error: {str(e)}")
        raise ClaimProcessingError(f"Database operation failed: {str(e)}")
    finally:
        db.close()

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    retry_error_callback=lambda retry_state: system_logger.error(
        f"Failed after {retry_state.attempt_number} attempts: {retry_state.outcome._exception}"
    )
)
def create_or_get_task(db: sessionmaker, claim_request: ProcessClaimTask) -> Task:
    """Create or retrieve a task with proper error handling."""
    try:
        existing_task = db.query(Task).filter_by(claim_id=claim_request.claim_id).first()
        if existing_task:
            return existing_task
        
        new_task = Task(
            task_id=claim_request.task_id,
            claim_id=claim_request.claim_id,
            task_type="co_ai",
            status=TaskStatus.PENDING,
        )
        db.add(new_task)
        db.commit()
        db.refresh(new_task)
        return new_task
    except SQLAlchemyError as e:
        db.rollback()
        system_logger.error(f"Task creation/retrieval failed: {str(e)}")
        raise ClaimProcessingError(f"Failed to create/get task: {str(e)}")
    
def start_process_manager(id: int):
    """
    Robust message processing with comprehensive error handling.

    Args:
        id (int): Claim ID to process
    """
    claim_request = ProcessClaimTask(
        claim_id=id, task_id=f"task_{str(uuid.uuid4())}"
    )

    try:
        with database_session() as db:
            # Initialize task
            task = create_or_get_task(db, claim_request)
            
            # Fetch claim data with error handling
            try:
                claim_data = get_claim_from_database(task.claim_id)
                if not claim_data:
                    raise ClaimProcessingError(f"No claim found for ID: {task.claim_id}")
                
                claim_data["dateClaimFiled"] = _new_get_datetime(claim_data["createdAt"])
            except Exception as e:
                system_logger.error(f"Error fetching claim data: {str(e)}")
                raise ClaimProcessingError(f"Failed to fetch claim data: {str(e)}")

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
            # Type-specific claim data processing with validation
            try:
                claim_type = claim_data["claimType"].lower()
                if claim_type == "accident":
                    claim_data = AccidentClaimData(**claim_data)
                elif claim_type == "theft":
                    claim_data = TheftClaimData(**claim_data)
                else:
                    raise ClaimProcessingError(f"Unsupported claim type: {claim_type}")
            except Exception as e:
                system_logger.error(f"Error processing claim type: {str(e)}")
                raise ClaimProcessingError(f"Failed to process claim type: {str(e)}")

            # Update statuses with error handling
            try:
                update_claim_status_database(claim_id, status=TaskStatus.PENDING)
                task.status = TaskStatus.RUNNING
                db.commit()
                db.refresh(task)
                update_claim_status_database(claim_id, status=TaskStatus.RUNNING)
            except Exception as e:
                system_logger.error(f"Status update failed: {str(e)}")
                raise ClaimProcessingError(f"Failed to update status: {str(e)}")
            try:
                # Process claim workflow
                team_summaries: UpdateClaimsReportModel = UpdateClaimsReportModel()
                endworkflow:bool  = False
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
                    },
                    # interrupt_after=call_summary_team
                ):
                    if "__end__" not in s:
                        team_summaries,endworkflow = control_workflow(
                            db,
                            claim_data.model_dump(),
                            claim_id,
                            claim_request,
                            task,
                            s,
                            team_summaries,
                            endworkflow
                        )

                        if endworkflow:
                            system_logger.info(message="Summary team has completed processing.")
                            break

            except Exception as e:
                system_logger.error(f"Workflow processing failed: {str(e)}")
                raise ClaimProcessingError(f"Failed to process workflow: {str(e)}")
        
            # Cleanup
            try:
                delete_pdf(claim_data.model_dump()['policyNumber'],rag_path)
            except Exception as e:
                system_logger.error(f"PDF cleanup failed: {str(e)}")
    except ClaimProcessingError as e:
            system_logger.error(f"Claim processing error: {str(e)}")
            # Update status to failed if possible
            try:
                with database_session() as db:
                    update_claim_status_database(id, status=TaskStatus.FAILED)
                    task = db.query(Task).filter_by(claim_id=id).first()
                    if task:
                        task.status = TaskStatus.FAILED
                        db.commit()
            except Exception as cleanup_error:
                system_logger.error(f"Failed to update error status: {str(cleanup_error)}")
            return None
    except Exception as e:
        system_logger.error(f"Unexpected error: {str(e)}")
        return None


