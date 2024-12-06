# encoding: utf-8
import os
from pydantic_settings import BaseSettings
from src.config.appconfig import env_config



class Settings(BaseSettings):
    """
    This class extends the BaseSettings class from FastAPI.
    It contains the project definitions.

    Args:
        None.

    Returns:
        class: extends the settings class.
    """

    if env_config.env == "development":
        API_STR: str = "/api/v1"
    else:
        API_STR: str = "/api/v1"

    VERSION: str = "3.0.2"
    
    PROJECT_NAME: str = "MasteryHive Claims Processing Backend AI Server"

  

def get_setting():
    """
    Return the settings object.

    Args:
        None.

    Returns:
        class: extends the settings class.
    """
    return Settings()

