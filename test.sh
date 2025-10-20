#!/bin/bash
export PYTHONPATH=/app


pytest -v --color=yes

exec "$@"
