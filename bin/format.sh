#!/bin/bash
# Format code using black and isort
cd "$(dirname "$0")/.."
uv run black .
uv run isort .
