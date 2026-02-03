#!/bin/bash
cd "$(dirname "$0")/.."
source .venv/bin/activate &&

# Chạy pytest với coverage cho app/services và tạo báo cáo HTML
python3 -m pytest --cov=app/services --cov-report=html --cov-report=term tests/
