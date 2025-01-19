# claimsprocessing-ai-backend


generate proto

```python
    python -m grpc_tools.protoc \
        -I . \
        --python_out=./src/pb \
        --grpc_python_out=./src/pb \
        src/protos/claims_processing.proto
```


1. currency
2. date so that AI can format the date in document according e.g in the policy docuemnt period 11/01/2024 for nigeria is 11th of january but AI id trained in US format, so it sees it as 1st of november.
3. preloss photos location <-> Tyrone needs to provide an endpoint for this
4. policy document location <-> Tyrone needs to provide an endpoint for this 