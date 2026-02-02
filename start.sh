#!/bin/bash

# Activate virtual environment if it exists
if [ -d .venv ]; then
    source .venv/bin/activate
fi

# Load .env file, ignoring comments and empty lines
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Default port if APP_PORT is not set in .env
PORT=${APP_PORT:-60062}

echo "Starting Batch Executor on port: $PORT"

# Run uvicorn
uvicorn app.main:app --host 0.0.0.0 --port "$PORT"
