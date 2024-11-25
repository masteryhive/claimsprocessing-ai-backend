from fastapi import FastAPI, BackgroundTasks, HTTPException, status
from fastapi.responses import JSONResponse
import uvicorn
from src.ai.manager import rabbitmq_worker
import os

# Suppress logging warnings
os.environ["GRPC_VERBOSITY"] = "ERROR"
os.environ["GLOG_minloglevel"] = "2"

app = FastAPI()


@app.get("/")
def home():
    """Home endpoint."""
    return {
        "ApplicationName": "Claims AI Server",
        "ApplicationOwner": "MasteryHive AI",
        "ApplicationVersion": "1.0",
        "ApplicationEngineer": "Sam Ayo",
        "ApplicationStatus": "running...",
    }

@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

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


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0")
