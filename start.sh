#!/bin/bash

# Set default environment variables
export ENVIRONMENT=${ENVIRONMENT:-development}
export PORT=${PORT:-8000}
export WORKERS=${WORKERS:-1}
export LOG_LEVEL=${LOG_LEVEL:-INFO}
export TIMEOUT=${TIMEOUT:-120}

echo "Rodando o servidor"
uvicorn src.app:create_app --factory \
    --host 0.0.0.0 --port 8000 \
    --log-level debug \
    --reload
