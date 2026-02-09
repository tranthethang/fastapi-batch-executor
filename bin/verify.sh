#!/bin/bash

# Load environment variables if .env exists
if [ -f .env ]; then
    set -a
    source .env
    set +a
fi

PORT=${APP_PORT:-80}
BASE_URL="http://127.0.0.1:$PORT"

if [ -z "$GEMINI_API_KEY" ] && [ -z "$GOOGLE_API_KEY" ]; then
    echo "Warning: GEMINI_API_KEY or GOOGLE_API_KEY not set in current shell."
fi

echo "Checking basic health status..."
curl -s "$BASE_URL/health" | jq .

echo -e "\nChecking full health status (with dependencies)..."
curl -s "$BASE_URL/health?depends=1" | jq .
