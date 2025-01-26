from pydantic import BaseModel
from src.error_trace.errorlogger import system_logger
from src.services.dependencies.automation import AutomationServiceClient


class MarketSearchModel(BaseModel):
    searchTerms: str
    target_market: str
    email: str
    password: str
    login_required: bool


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

    def _run_healthcheck(self) -> str:
        if AutomationServiceClient().wait_for_ready():
            return AutomationServiceClient().health_check()
        else:
            system_logger.error(error="Failed to establish connection")


# m = MarketSearchModel(
#     email="sam@masteryhive.ai",
#     login_required=True,
#     password="JLg8m4aQ8n46nhC",
#     searchTerms="[['toyota camry headlight tokunbo',467880],['toyota camry headlight brand new',467880]]",
#     target_market="jiji"
# )
# client = AutomationServiceLogic()
# result = client._run_market_search(marketSearchModel=m)
# print(result)