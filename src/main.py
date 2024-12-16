from fastapi import FastAPI, BackgroundTasks, HTTPException, status
from fastapi.responses import JSONResponse, PlainTextResponse
import uvicorn,os
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from src.error_trace.errorlogger import LOG_FILE, log_error
from src.ai.model import init_vertexai
from src.config.db_setup import SessionLocal
from src.ai.claims_processing.manager import rabbitmq_worker
from src.config.settings import get_setting
from src.config.appconfig import env_config
from src.utilities.Printer import printer
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware

# Suppress logging warnings
os.environ["GRPC_VERBOSITY"] = "ERROR"
os.environ["GLOG_minloglevel"] = "2"

# Get application settings
settings = get_setting()

# Description for API documentation
description = f"""
{settings.API_STR} helps you do awesome stuff. 🚀
"""


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Context manager for application lifespan.
    This function initializes and cleans up resources during the application's lifecycle.
    """
    init_vertexai()
    print(running_mode)
    print()
    printer(" ⚡️🚀 AI Server::Started", "sky_blue")
    print()
    printer(" ⚡️🏎  AI Server::Running", "sky_blue")
    yield
    printer(" ⚡️🚀 AI Server::SHUTDOWN", "red")


# Create FastAPI app instance
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=description,
    openapi_url=f"{settings.API_STR}/openapi.json",
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
    lifespan=lifespan,
)


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Configure for development or production mode
if env_config.env == "development" or env_config.env == "local":
    running_mode = "  👩‍💻 🛠️  Running in::development mode"
else:
    app.add_middleware(HTTPSRedirectMiddleware)
    running_mode = "  🏭 ☁  Running in::production mode"

# Origins for CORS
origins = ["*"]

# Add middleware to allow CORS requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["POST", "GET", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)


@app.get("/")
def home():
    """Home endpoint."""
    return {
        "ApplicationName": "Claims AI BackEnd Server",
        "ApplicationOwner": "MasteryHive AI",
        "ApplicationVersion": "1.0",
        "ApplicationEngineer": "Sam Ayo",
        "ApplicationStatus": "running...",
    }

@app.get("/health", status_code=status.HTTP_200_OK)
def APIHealth():
    """
    Returns a dictionary containing information about the application.
    """
    return "healthy"

@app.get("/view-logs/", response_class=PlainTextResponse)
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
    uvicorn.run(app, host="0.0.0.0",port=env_config.app_port)
