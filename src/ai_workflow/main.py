import logging
from concurrent import futures

import grpc
from ai_models.model import init_vertexai
from grpc_interceptor import ExceptionToStatusInterceptor

from config.settings import Settings
from pb.claims_processing_pb2_grpc import add_ClaimsProcessingServicer_to_server
from services.ai_workflow import ClaimsProcessingBaseService

settings = Settings()

init_vertexai()

class ClaimProcessingService(ClaimsProcessingBaseService):
    pass


def serve():
    interceptors = [ExceptionToStatusInterceptor()]
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10), interceptors=interceptors
    )
    add_ClaimsProcessingServicer_to_server(ClaimProcessingService(), server)
    server.add_insecure_port("[::]:50051")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    # logging.basicConfig(level=settings.LOGGING_LEVEL, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logging.basicConfig(level=settings.LOGGING_LEVEL, format='%(asctime)s - %(levelname)s - %(message)s')
    logging.info('⚡️🚀 Claim Processing workflow Server Starter...')

    serve()