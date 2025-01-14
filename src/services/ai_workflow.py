from grpc import StatusCode
from grpc_interceptor.exceptions import NotFound, GrpcException
from google.protobuf.empty_pb2 import Empty
from src.pb.claims_processing_pb2 import HealthCheckResponse 
from src.workflow_orch.manager import process_message
from src.pb.claims_processing_pb2_grpc import ClaimsProcessingServicer




class ClaimsProcessingBaseService(ClaimsProcessingServicer):
    
    def ProcessClaim(self, request, context):
        try:
            print(int(request.claimId))
            process_message(int(request.claimId))
        except Exception as e:
            raise GrpcException(status_code=StatusCode.INTERNAL, details=str(e))
        return Empty() 
    
    def HealthCheck(self, request, context):
        """Health check endpoint"""
        return HealthCheckResponse(status="healthy")