# Use the official Python image as a parent image for the build stage
FROM python:3.12-slim AS builder

# Set the working directory in the container
WORKDIR /app

# Install system dependencies and Chrome
RUN apt-get update && apt-get install -y \
    wget \
    && wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && apt-get install -y ./google-chrome-stable_current_amd64.deb \
    && rm google-chrome-stable_current_amd64.deb \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN apt-get install -y \
    libx11-dev \
    libxkbfile-dev \
    libsecret-1-dev \
    libnss3 \
    fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables for the build stage
ENV PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_NO_CACHE_DIR=off \
    PYTHONUNBUFFERED=1

RUN pip install "poetry" "pytest-playwright" "playwright"

RUN playwright install

# Copy requirements to install dependencies in the builder stage
# COPY requirements.txt .
COPY pyproject.toml poetry.lock* /app/

# Configure Poetry:
# - No virtualenvs inside the docker container
# - Do not ask any interactive questions
RUN poetry config virtualenvs.create false \
    && poetry install --only main --no-interaction --no-ansi

# Install dependencies
# RUN pip install --no-cache-dir -r requirements.txt

# Use the official Python image as a parent image for the runtime stage
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies and Chrome
RUN apt-get update && apt-get install -y \
    wget \
    && wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && apt-get install -y ./google-chrome-stable_current_amd64.deb \
    && rm google-chrome-stable_current_amd64.deb \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y \
    libx11-dev \
    libxkbfile-dev \
    libsecret-1-dev \
    libnss3 \
    fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables for the runtime stage
ENV ENV="production" \
    PYTHONUNBUFFERED=1

# Copy the installed dependencies from the builder stage to the runtime stage
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy the pyproject.toml and poetry.lock files from the builder stage
COPY --from=builder /app/pyproject.toml /app/poetry.lock* /app/

# Install Playwright browsers
RUN poetry run playwright install chromium \
    && poetry run playwright install-deps chromium

RUN playwright install

# Copy the application code into the container
COPY . /app

EXPOSE 8080

# Use startup file for production
CMD ["python","-m", "src.main"]
