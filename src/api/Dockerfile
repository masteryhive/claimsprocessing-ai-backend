# Use the official Python image as a parent image for the build stage
FROM python:3.12-slim AS builder

# Set the working directory in the container
WORKDIR /home/api

# Set environment variables for the build stage
ENV PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_NO_CACHE_DIR=off \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

RUN pip install "poetry"

# Copy requirements to install dependencies in the builder stage
# COPY requirements.txt .
COPY pyproject.toml poetry.lock* ./

# Configure Poetry:
# - No virtualenvs inside the docker container
# - Do not ask any interactive questions
RUN poetry config virtualenvs.create false \
    && poetry install --only main --no-interaction --no-ansi --no-cache --no-root


# Use the official Python image as a parent image for the runtime stage
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /home/api

# Set environment variables for the runtime stage
ENV ENV="production" \
    PYTHONUNBUFFERED=1

# Copy the installed dependencies from the builder stage to the runtime stage
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
    
# Copy the application code into the container
COPY . .

EXPOSE 8080

# Use uvicorn to serve FastAPI without auto-reload for production
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
