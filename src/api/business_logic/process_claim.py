
from dependencies.grpc.ai_workflow import ClaimProcessingClient


class ProcessClaimLogic:
    def _run_processing(self, claim_id: str):
        return ClaimProcessingClient().process_claim(claim_id=claim_id)