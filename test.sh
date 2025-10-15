#!/bin/bash
export PYTHONPATH=/app
pytest -v
exec "$@"
