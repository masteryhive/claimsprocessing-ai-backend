import asyncio
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
    
    async def _run_niid_check(self, registrationNumber: str):
        async with AutomationServiceClient() as client:
            # First check health status
            health_status = await client.health_check()
            if health_status['status'] != "healthy":
                system_logger.error(error="Health check failed before NIID check")
                return {"error": "Service health check failed"}
                
            return await client.niid_check(registrationNumber=registrationNumber)
        
    async def _run_vin_check(self, VehicleIdentificationNumber: str):
        async with AutomationServiceClient() as client:
            # First check health status
            health_status = await client.health_check()
            if health_status['status'] != "healthy":
                system_logger.error(error="Health check failed before VIN check")
                return {"error": "Service health check failed"}
            return await client.vin_check(VehicleIdentificationNumber=VehicleIdentificationNumber)
        
    async def _run_healthcheck(self) -> str:
        async with AutomationServiceClient() as client:
            return await client.health_check()


# async def r():
#     client = AutomationServiceLogic()
#     result = await client._run_healthcheck()
#     print(result)




# asyncio.run(r())