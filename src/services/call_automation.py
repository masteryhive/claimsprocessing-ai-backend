from pydantic import BaseModel
from src.error_trace.errorlogger import system_logger
from src.services.dependencies.automation import AutomationServiceClient

# Base Model for Market Search
class MarketSearchModel(BaseModel):
    searchTerms: str
    target_market: str
    email: str
    password: str
    login_required: bool

# Class for Automation Logic
class AutomationServiceLogic:
    def _run_market_search(self, marketSearchModel: MarketSearchModel):
        if AutomationServiceClient().wait_for_ready():
            return AutomationServiceClient().market_search(
                searchTerms=marketSearchModel.searchTerms,
                target_market=marketSearchModel.target_market,
                email=marketSearchModel.email,
                password=marketSearchModel.password,
                login_required=marketSearchModel.login_required,
            )
        else:
            system_logger.error(error="Failed to establish connection")
    
    def _run_niid_check(self, registrationNumber: str):
        if AutomationServiceClient().wait_for_ready():
            return AutomationServiceClient().niid_check(
                registrationNumber=registrationNumber
            )
        else:
            system_logger.error(error="Failed to establish connection")

    def _run_healthcheck(self) -> str:
        if AutomationServiceClient().wait_for_ready():
            return AutomationServiceClient().health_check()
        else:
            system_logger.error(error="Failed to establish connection")
