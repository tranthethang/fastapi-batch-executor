#!/bin/bash

# Activate virtual environment if it exists
if [ -d .venv ]; then
    source .venv/bin/activate
fi

# Install formatting tools
pip install black isort

echo "Running isort..."
isort .

echo "Running black..."
black .

echo "Format complete!"
