# claimsprocessing-ai-backend


generate proto

```python
    python -m grpc_tools.protoc \
        -I . \
        --python_out=./src/pb \
        --grpc_python_out=./src/pb \
        src/protos/claims_processing.proto
```