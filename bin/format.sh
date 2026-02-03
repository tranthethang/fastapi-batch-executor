#!/bin/bash
# Format code using black and isort
cd "$(dirname "$0")/.."
source .venv/bin/activate &&

black .

isort .
