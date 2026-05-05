#!/bin/bash
cd "$(dirname "$0")/.."

# Chạy pytest với coverage cho app sử dụng uv và PYTHONPATH=.
PYTHONPATH=. uv run pytest --cov=app --cov-report=term --cov-fail-under=90 tests/
