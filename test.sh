#!/bin/bash
export PYTHONPATH=/app
echo "run tests __"
pytest -v
exec "$@"
