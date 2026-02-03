#!/bin/bash

# Get the directory where the script is located and move to the project root
PARENT_PATH=$(cd "$(dirname "$0")/.." ; pwd -P)
cd "$PARENT_PATH"

# Load the APP_PORT variable from the .env file
if [ -f .env ]; then
  # Extract the value of APP_PORT using grep and cut
  PORT=$(grep '^APP_PORT=' .env | cut -d '=' -f2)
else
  echo "Error: .env file not found at $PARENT_PATH"
  exit 1
fi

# Validate that the PORT variable is not empty
if [ -z "$PORT" ]; then
  echo "Error: APP_PORT is not defined in the .env file."
  exit 1
fi

# Find the Process ID (PID) running on the specified port
PID=$(lsof -t -i:"$PORT")

if [ -z "$PID" ]; then
  echo "Process not found: Port $PORT is already free."
else
  echo "Stopping FastAPI application (PID: $PID) on port $PORT..."
  
  # Force kill the process
  kill -9 $PID
  
  if [ $? -eq 0 ]; then
    echo "Successfully stopped the application."
  else
    echo "Error: Failed to stop the application."
  fi
fi