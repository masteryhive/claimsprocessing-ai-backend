import contextlib
import datetime
import logging
from concurrent import futures
import multiprocessing
import os,socket,sys,time,grpc,platform
from src.ai_models.model import init_vertexai
from grpc_interceptor import ExceptionToStatusInterceptor

from src.config.settings import Settings
from src.config.appconfig import env_config
from src.pb.claims_processing_pb2_grpc import add_ClaimsProcessingServicer_to_server
from src.services.ai_workflow import ClaimsProcessingBaseService

settings = Settings()

_LOGGER = logging.getLogger(__name__)
_PROCESS_COUNT = multiprocessing.cpu_count()
_ONE_DAY = datetime.timedelta(days=1)

class ClaimProcessingService(ClaimsProcessingBaseService):
    pass

def _wait_forever(server):
    try:
        while True:
            time.sleep(_ONE_DAY.total_seconds())
    except KeyboardInterrupt:
        server.stop(None)


def create_server(bind_address:str):
    interceptors = [ExceptionToStatusInterceptor()]
    if platform.system() == "Windows":
        server = grpc.server(
            futures.ThreadPoolExecutor(max_workers=1),  # Increased worker threads instead of processes
            interceptors=interceptors
        )
    else:
        options = (("grpc.so_reuseport", 1),)
        server = grpc.server(
            futures.ThreadPoolExecutor(max_workers=10), interceptors=interceptors,
            options=options,
        )
    add_ClaimsProcessingServicer_to_server(ClaimProcessingService(), server)
    server.add_insecure_port(bind_address)
    server.start()
    try:
        # Keep the server running
        _wait_forever(server)
    except KeyboardInterrupt:
        server.stop(0)
        _LOGGER.info("Server stopped gracefully")
    # server.wait_for_termination()
    


def main():
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    _LOGGER.addHandler(handler)
    _LOGGER.setLevel(settings.LOGGING_LEVEL)

    # Initialize VertexAI
    init_vertexai()

    # Get port from environment or config
    port = int(os.environ.get("PORT", env_config.app_port))

    _LOGGER.info(f"⚡️🚀 Starting Claim Processing workflow Server ::{port}...")
    sys.stdout.flush()

    bind_address = "[::]:{}".format(port)

    if platform.system() == "Windows":
        # Create and start server
        worker = multiprocessing.Process(target=create_server, args=(bind_address,))
        worker.start()
        worker.join()
    else:
        workers = []
        for _ in range(_PROCESS_COUNT):
            # NOTE: It is imperative that the worker subprocesses be forked before
            # any gRPC servers start up. See
            # https://github.com/grpc/grpc/issues/16001 for more details.
            worker = multiprocessing.Process(
                target=create_server, args=(bind_address,)
            )
            worker.start()
            workers.append(worker)
        for worker in workers:
            worker.join()
        _LOGGER.info(f"Server started successfully on port {port}")

            
if __name__ == "__main__":
    main()
