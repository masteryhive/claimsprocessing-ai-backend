import grpc
from google.protobuf import empty_pb2
from google.protobuf.json_format import MessageToDict
from src.config.appconfig import env_config
from src.pb.automation_service.service_pb2 import HealthCheckRequest, LocalMarketRequest,NIIDCheckRequest
from src.pb.automation_service.service_pb2_grpc import AutomationServiceStub
from src.error_trace.errorlogger import system_logger

# gRPC Client for interacting with the Automation Service.
class AutomationServiceClient(object):
    def __init__(self):
        # Create credentials for secure channel
        credentials = grpc.ssl_channel_credentials()

        # Format the URL properly for gRPC (remove https:// if present)
        target = env_config.automation_service_api
        target = "localhost:4000"
        if target.startswith("https://"):
            target = target.replace("https://", "")

        # Create secure channel with proper options
        options = (
            ("grpc.ssl_target_name_override", target),
            ("grpc.max_receive_message_length", 1024 * 1024 * 100),  # 100MB
            ("grpc.max_send_message_length", 1024 * 1024 * 100),  # 100MB
        )

        self.channel = grpc.insecure_channel(target, options=options)
        if env_config.env != "local":
            self.channel = grpc.secure_channel(target, credentials, options=options)
        self.stub = AutomationServiceStub(self.channel)

    def __del__(self):
        if hasattr(self, "channel"):
            self.channel.close()
    #Performs a market search request 
    def market_search(
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
            response = self.stub.MarketSearch(
                LocalMarketRequest(
                    targetMarket=target_market,
                    email=email,
                    password=password,
                    searchTerms=searchTerms,
                    loginRequired=login_required,
                )
            )

            return MessageToDict(
                response,  # Changed from empty_pb2.Empty() to actual response
                preserving_proto_field_name=True,
            )

        except grpc.RpcError as rpc_error:
            error_message = (
                f"RPC Error: {rpc_error.details()} (code: {rpc_error.code()})"
            )
            system_logger.error(error=error_message)
            return {"error": error_message}
    # Initiates a vehicle insurance check (NIID check) using the provided registration number.
    def niid_check(
        self,
        registrationNumber: str,
    ):
        try:
            system_logger.info(
                message=f"Starting worker for niid check: {registrationNumber}"
            )
            response = self.stub.NIIDCheck(
                NIIDCheckRequest(
                    registrationNumber=registrationNumber
                )
            )

            return MessageToDict(
                response,  # Changed from empty_pb2.Empty() to actual response
                preserving_proto_field_name=True,
            )

        except grpc.RpcError as rpc_error:
            error_message = (
                f"RPC Error: {rpc_error.details()} (code: {rpc_error.code()})"
            )
            system_logger.error(error=error_message)
            return {"error": error_message}
    # Checks the health status of the Automation Service.  
    def health_check(self):
        try:
            response = self.stub.HealthCheck(HealthCheckRequest())

            return MessageToDict(
                response,
                preserving_proto_field_name=True,
            )

        except grpc.RpcError as rpc_error:
            error_message = (
                f"Health Check Error: {rpc_error.details()} (code: {rpc_error.code()})"
            )
            system_logger.error(error=error_message)
            return {"error": error_message}

    def wait_for_ready(self, timeout=30):
        """Wait for the channel to be ready"""
        try:
            grpc.channel_ready_future(self.channel).result(timeout=timeout)
            return True
        except grpc.FutureTimeoutError:
            system_logger.error(
                error=f"Channel failed to become ready within {timeout} seconds"
            )
            return False
