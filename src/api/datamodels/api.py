from pydantic import BaseModel, Field
from typing import Any, List, Optional, Dict, Union
from datetime import datetime


# Data model for input validation
class ClaimRequest(BaseModel):
    claimId: str
