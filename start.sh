#!/bin/bash

export ENVIRONMENT=${ENVIRONMENT:-development}
export PORT=${PORT:-8000}
export WORKERS=${WORKERS:-1}
export LOG_LEVEL=${LOG_LEVEL:-warning}
export TIMEOUT=${TIMEOUT:-120}

# Normaliza o nível de log para minúsculas
LOG_LEVEL=$(echo "$LOG_LEVEL" | tr '[:upper:]' '[:lower:]')

echo "Running the server ($ENVIRONMENT)"

# Comando base do Gunicorn usando o worker uvicorn
GUNICORN_CMD=(
  gunicorn "src.app:create_app()"
  --worker-class uvicorn.workers.UvicornWorker
  --bind "0.0.0.0:$PORT"
  --workers "$WORKERS"
  --timeout "$TIMEOUT"
  --log-level "$LOG_LEVEL"
)

# Adiciona reload em modo de desenvolvimento
if [ "$ENVIRONMENT" = "development" ]; then
  GUNICORN_CMD+=(--reload)
fi

exec "${GUNICORN_CMD[@]}"
