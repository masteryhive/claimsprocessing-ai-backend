from grpc import StatusCode
from grpc_interceptor.exceptions import NotFound, GrpcException
from google.protobuf.empty_pb2 import Empty
from src.pb.claims_processing_pb2 import HealthCheckResponse,LogViewResponse
from src.workflow_orch.manager import start_process_manager
from src.pb.claims_processing_pb2_grpc import ClaimsProcessingServicer
import threading,logging
from concurrent.futures import ThreadPoolExecutor
from queue import Queue
from prometheus_client import Counter, Histogram, Gauge
import pybreaker
from src.error_trace.errorlogger import system_logger


class ClaimsProcessingBaseService(ClaimsProcessingServicer):
    def __init__(self):
        self.thread_pool = ThreadPoolExecutor(max_workers=10)
        self.processing_queue = Queue()
        # Start background worker
        self.worker_thread = threading.Thread(target=self._process_queue, daemon=True)
        self.worker_thread.start()
    
    def ProcessClaim(self, request, context):
        try:
            claim_id = int(request.claimId)
            system_logger.info(f"Received claim processing request for ID: {claim_id}")
            
            # Submit the task to the queue
            self.processing_queue.put(claim_id)
            
            system_logger.info(f"Successfully queued claim ID: {claim_id} for processing")
            return Empty()
            
        except ValueError as e:
            system_logger.error(f"Invalid claim ID format: {request.claimId}")
            raise GrpcException(
                status_code=StatusCode.INVALID_ARGUMENT, 
                details=f"Invalid claim ID format: {str(e)}"
            )
        except Exception as e:
            system_logger.error(f"Unexpected error while queueing claim: {str(e)}")
            raise GrpcException(
                status_code=StatusCode.INTERNAL, 
                details=f"Internal server error: {str(e)}"
            )

    def _process_queue(self):
        """Background worker that processes claims from the queue"""
        while True:
            try:
                claim_id = self.processing_queue.get()
                system_logger.info(f"Processing claim ID: {claim_id}")
                
                # Submit the actual processing to thread pool
                self.thread_pool.submit(self._process_single_claim, claim_id)
                
            except Exception as e:
                system_logger.error(f"Error in queue processing: {str(e)}")
            finally:
                self.processing_queue.task_done()

    def _process_single_claim(self, claim_id):
        """Process a single claim with error handling"""
        try:
            start_process_manager(claim_id)
            system_logger.info(f"Successfully processed claim ID: {claim_id}")
        except Exception as e:
            system_logger.error(f"Error processing claim ID {claim_id}: {str(e)}")
    
    def HealthCheck(self, request, context):
        """Health check endpoint"""
        return HealthCheckResponse(status="healthy")
    
    def ViewLogs(self, request, context):
        """Retrieve log files based on the log type."""
        try:
            log_type = request.log_type.lower()
            if log_type not in ["error", "info"]:
                context.abort(
                    StatusCode.INVALID_ARGUMENT,
                    f"Invalid log_type: {log_type}. Must be 'error' or 'info'."
                )
            log_data = system_logger.view_logs(log_type=log_type)
            return LogViewResponse(logs=log_data)
        except Exception as e:
            raise GrpcException(
                status_code=StatusCode.INTERNAL,
                details=f"Failed to retrieve logs: {str(e)}"
            )
    
    def __del__(self):
        """Cleanup resources on service shutdown"""
        try:
            self.thread_pool.shutdown(wait=False)
        except Exception as e:
            system_logger.error(f"Error during thread pool shutdown: {str(e)}")