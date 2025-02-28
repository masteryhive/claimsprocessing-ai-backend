import asyncio
import grpc
from src.config.appconfig import env_config
from grpc.aio import insecure_channel, secure_channel
from google.protobuf.json_format import MessageToDict
from src.pb.automation_service.service_pb2 import HealthCheckRequest, LocalMarketRequest, NIIDCheckRequest
from src.pb.automation_service.service_pb2_grpc import AutomationServiceStub
from src.error_trace.errorlogger import system_logger

class AutomationServiceClient:
    def __init__(self):
        self.target = env_config.automation_service_api
      
        # Properly format the target URL
        if self.target.startswith("https://"):
            self.target = self.target.replace("https://", "")
        
        # Configure proper channel options
        self.options = [
            ("grpc.enable_http_proxy", 0),
            ("grpc.enable_https_proxy", 0),
            ("grpc.keepalive_time_ms", 30000),
            ("grpc.keepalive_timeout_ms", 10000),
            ("grpc.keepalive_permit_without_calls", 1),
            ("grpc.http2.min_time_between_pings_ms", 10000),
            ("grpc.http2.max_pings_without_data", 0),
            ("grpc.max_receive_message_length", 1024 * 1024 * 100),
            ("grpc.max_send_message_length", 1024 * 1024 * 100),
        ]

        # Add SSL target override only for production
        if env_config.env != "local":
            self.options.append(("grpc.ssl_target_name_override", self.target))
            
        self.channel = None
        self.stub = None
        
    async def __aenter__(self):
        if env_config.env != "local":
            self.channel = secure_channel(
                target=self.target,
                credentials=grpc.ssl_channel_credentials(),
                options=self.options
            )
        else:
            self.channel = insecure_channel(
                target=self.target,
                options=self.options
            )
            
        self.stub = AutomationServiceStub(self.channel)
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if self.channel:
            await self.channel.close()

    async def market_search(
        self,
        searchTerms: str,
        target_market: str,
        email: str,
        password: str,
        login_required: bool,
    ):
        try:
            system_logger.info(
                message=f"Starting worker for market search: {searchTerms}"
            )
            
            # Set timeout for the RPC call
            timeout = 30  # seconds
            response = await self.stub.MarketSearch(
                request=LocalMarketRequest(
                    targetMarket=target_market,
                    email=email,
                    password=password,
                    searchTerms=searchTerms,
                    loginRequired=login_required,
                ),
                timeout=timeout,
                wait_for_ready=True
            )

            return MessageToDict(
                response,
                preserving_proto_field_name=True,
            )

        except grpc.RpcError as rpc_error:
            error_message = f"RPC Error: {rpc_error.details()} (code: {rpc_error.code()})"
            system_logger.error(error=error_message)
            return {"error": error_message}
        except Exception as e:
            error_message = f"Unexpected error in market_search: {str(e)}"
            system_logger.error(error=error_message)
            return {"error": error_message}

    async def niid_check(self, registrationNumber: str):
        try:
            system_logger.info(
                message=f"Starting worker for niid check: {registrationNumber}"
            )
            
            timeout = 90  # seconds
            response = await self.stub.NIIDCheck(
                request=NIIDCheckRequest(registrationNumber=registrationNumber),
                timeout=timeout,
                wait_for_ready=True
            )

            return MessageToDict(response, preserving_proto_field_name=True)

        except grpc.RpcError as rpc_error:
            error_message = f"RPC Error: {rpc_error.details()} (code: {rpc_error.code()})"
            system_logger.error(error=error_message)
            return {"error": error_message}
        except Exception as e:
            error_message = f"Unexpected error in niid_check: {str(e)}"
            system_logger.error(error=error_message)
            return {"error": error_message}

    async def health_check(self):
        try:
            timeout = 40  # seconds
            response = await self.stub.HealthCheck(
                request=HealthCheckRequest(),
                timeout=timeout,
                wait_for_ready=True
            )
            return MessageToDict(response, preserving_proto_field_name=True)

        except grpc.RpcError as rpc_error:
            error_message = f"Health Check Error: {rpc_error.details()} (code: {rpc_error.code()})"
            system_logger.error(error=error_message)
            return {"error": error_message}
        except Exception as e:
            error_message = f"Unexpected error in health_check: {str(e)}"
            system_logger.error(error=error_message)
            return {"error": error_message}