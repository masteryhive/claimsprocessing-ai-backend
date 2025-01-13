import grpc
from google.protobuf.json_format import MessageToDict

from config.settings import Settings
from pb.claims_processing_pb2 import ClaimsRequest
from pb.claims_processing_pb2_grpc import ClaimsProcessingStub

settings = Settings()
class ClaimProcessingClient(object):
    def __init__(self):
        self.channel = grpc.insecure_channel(f"{settings.GRPC_AI_WORKFLOW}:50051")
        self.stub = ClaimsProcessingStub(self.channel)

    def process_claim(self, claim_id):
        try:
            stub = self.stub.ProcessClaim(ClaimsRequest(claimId=claim_id))

            return MessageToDict(
                stub,
                preserving_proto_field_name=True,
 
            )

        except grpc.RpcError as rpc_error:
            return {
                "error": rpc_error.details()
            }