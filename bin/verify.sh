#!/bin/bash

# Load environment variables if .env exists
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

PORT=${APP_PORT:-80}
BASE_URL="http://127.0.0.1:$PORT"

echo "Checking basic health status..."
curl -s "$BASE_URL/health" | jq .

echo -e "\nChecking full health status (with dependencies)..."
curl -s "$BASE_URL/health?depends=1" | jq .
