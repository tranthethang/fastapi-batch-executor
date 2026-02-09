#!/bin/bash
cd "$(dirname "$0")/.."
source .venv/bin/activate &&

# Chạy pytest với coverage cho app và tạo báo cáo HTML
python -m pytest --cov=app --cov-report=term tests/
