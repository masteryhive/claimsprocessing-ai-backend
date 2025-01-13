from grpc import StatusCode
from grpc_interceptor.exceptions import NotFound, GrpcException
from google.protobuf.empty_pb2 import Empty

# from manager import process_message
from manager import process_message
from pb.claims_processing_pb2_grpc import ClaimsProcessingServicer




class ClaimsProcessingBaseService(ClaimsProcessingServicer):

    def ProcessClaim(self, request, context):
        try:
            process_message(int(request.claimId))
        except Exception as e:
            raise GrpcException(status_code=StatusCode.INTERNAL, details=str(e))
        return Empty() 