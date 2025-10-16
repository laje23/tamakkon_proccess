#!/bin/bash
export PYTHONPATH=/app
echo "run all tests in tests/"
pytest tests/ -v
exec "$@"

