from fastapi import FastAPI, BackgroundTasks, HTTPException, status
from fastapi.responses import JSONResponse, PlainTextResponse
import uvicorn,os
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from routes.ai_workflow import router
from config.db_setup import SessionLocal
# from ai_workflow.manager import rabbitmq_worker
import pkg_resources
from config.settings import Settings
from config.appconfig import env_config
from utilities.Printer import printer
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware
from google.protobuf import __version__ as protobuf_version

# Suppress logging warnings
os.environ["GRPC_VERBOSITY"] = "ERROR"
os.environ["GLOG_minloglevel"] = "2"

# Get application settings
settings = Settings()

# Description for API documentation
description = f"""
{settings.API_STR} helps you do awesome stuff. 🚀
"""

# Add version check before app initialization
def check_protobuf_version():
    required_version = "5.29.0"  # Version that matches your generated code
    current_version = protobuf_version
    if pkg_resources.parse_version(current_version) < pkg_resources.parse_version(required_version):
        printer(f" ⚠️  Warning: Protobuf version mismatch. Required: {required_version}, Current: {current_version}", "yellow")
        printer(" ⚠️  Please run: pip install --upgrade protobuf==5.29.0", "yellow")
        raise RuntimeError("Incompatible Protobuf version")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Context manager for application lifespan.
    This function initializes and cleans up resources during the application's lifecycle.
    """
    check_protobuf_version()
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

app.include_router(router, prefix=settings.API_PREFIX)

# @app.post("/start-worker",status_code=status.HTTP_202_ACCEPTED)
# def start_worker(background_tasks: BackgroundTasks,):
#     """HTTP endpoint to start the RabbitMQ worker."""
#     try:
#         background_tasks.add_task(rabbitmq_worker)
#         return JSONResponse(
#             status_code=status.HTTP_202_ACCEPTED,
#             content={"status": "Worker started successfully"},
#         )
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

    
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0",port=env_config.app_port)
