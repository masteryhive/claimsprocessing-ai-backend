# Load .env file using:
from dotenv import load_dotenv
load_dotenv(override=True)
import os

class EnvConfig:
    """Class to hold environment configuration variables."""
    
    def __init__(self):
        self.env = os.getenv("PYTHON_ENV")
        self.app_port = os.getenv("PORT")
        self.backend_api = os.getenv("APP_BACKEND_API")
        self.auth_user = os.getenv("AUTH_USERNAME")
        self.auth_password = os.getenv("AUTH_PASSWORD")
        self.project_id = os.getenv("PROJECT_ID")
        self.region = os.getenv("REGION")
        self.staging_bucket = os.getenv("STAGING_BUCKET")
        self.host = os.getenv("DB_HOST")
        self.database = os.getenv("DB_DATABASE")
        self.user = os.getenv("DB_USER")
        self.password = os.getenv("DB_PASSWORD")
        self.automation_service_api = os.getenv("AUTOMATION_SERVICE_API")
        

        
    def __repr__(self):
        return (
            f"EnvConfig(env={self.env}, app_port={self.app_port}, "
            f"auth_user={self.auth_user}, auth_password=**** "
            f"project_id={self.project_id}, region={self.region}, "
            f"staging_bucket={self.staging_bucket}, host={self.host}, "
            f"database={self.database}, user={self.user}, password=****)"
            f"backend_api={self.backend_api}, "
        )

# Create an instance of EnvConfig to access the environment variables
env_config = EnvConfig()