import contextlib
import datetime
import logging
from concurrent import futures
import multiprocessing
import os
import socket
import sys
import time

import grpc
from src.ai_models.model import init_vertexai
from grpc_interceptor import ExceptionToStatusInterceptor

from src.config.settings import Settings
from src.config.appconfig import env_config
from src.pb.claims_processing_pb2_grpc import add_ClaimsProcessingServicer_to_server
from src.services.ai_workflow import ClaimsProcessingBaseService

settings = Settings()

init_vertexai()

_LOGGER = logging.getLogger(__name__)
_PROCESS_COUNT = multiprocessing.cpu_count()
_THREAD_CONCURRENCY = _PROCESS_COUNT
_ONE_DAY = datetime.timedelta(days=1)

class ClaimProcessingService(ClaimsProcessingBaseService):
    pass

port = os.environ.get("PORT", env_config.app_port)

def _wait_forever(server):
    try:
        while True:
            time.sleep(_ONE_DAY.total_seconds())
    except KeyboardInterrupt:
        server.stop(None)


def _run_server(bind_address):
    interceptors = [ExceptionToStatusInterceptor()]
    options = (("grpc.so_reuseport", 1),)
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10), interceptors=interceptors,
          options=options,
    )
    add_ClaimsProcessingServicer_to_server(ClaimProcessingService(), server)
    server.add_insecure_port(bind_address)
    server.start()
    _wait_forever(server)
    # server.wait_for_termination()
    


def main():

    bind_address = "[::]:{}".format(port)
    _LOGGER.info("Binding to '%s'", bind_address)
    # logging.basicConfig(level=settings.LOGGING_LEVEL, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logging.basicConfig(level=settings.LOGGING_LEVEL, format='%(asctime)s - %(levelname)s - %(message)s')
    logging.info(f"⚡️🚀 Claim Processing workflow Server Starter::{port}...")
    sys.stdout.flush()
    workers = []
    for _ in range(_PROCESS_COUNT):
        # NOTE: It is imperative that the worker subprocesses be forked before
        # any gRPC servers start up. See
        # https://github.com/grpc/grpc/issues/16001 for more details.
        worker = multiprocessing.Process(
            target=_run_server, args=(bind_address,)
        )
        worker.start()
        workers.append(worker)
    for worker in workers:
        worker.join()
            
if __name__ == "__main__":
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter("[PID %(process)d] %(message)s")
    handler.setFormatter(formatter)
    _LOGGER.addHandler(handler)
    _LOGGER.setLevel(logging.INFO)
    main()