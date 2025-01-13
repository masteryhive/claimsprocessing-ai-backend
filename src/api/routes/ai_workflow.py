import os
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from fastapi.responses import JSONResponse, PlainTextResponse
from business_logic.process_claim import ProcessClaimLogic
from datamodels.api import ClaimRequest
from error_trace.errorlogger import LOG_FILE, log_error

router = APIRouter()

@router.get("/view-logs/", response_class=PlainTextResponse)
async def view_logs():
    """
    Read and return the contents of systems.log in plain text.
    """
    try:
        if not os.path.exists(LOG_FILE):
            raise HTTPException(status_code=404, detail="Log file not found.")

        with open(LOG_FILE, "r") as log_file:
            logs = log_file.read()
        return logs or "Log file is empty."
    except Exception as e:
        log_error(f"Error reading log file: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to read log file: {e}")
    
@router.post(
    "/start-direct-worker",
    name="start-ai-workflow",
)
def start_worker(claim_request:ClaimRequest,background_tasks: BackgroundTasks,process_claim_logic: ProcessClaimLogic = Depends(ProcessClaimLogic),):
    background_tasks.add_task(process_claim_logic._run_processing, claim_id=claim_request.claimId)
    return JSONResponse(
            status_code=status.HTTP_202_ACCEPTED,
            content={"status": "Worker started successfully"},
        )