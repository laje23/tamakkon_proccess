#!/bin/bash

echo "wait for database connection ..."
until pg_isready -h "$PGHOST" -p "5432" >/dev/null 2>&1; do
  echo "Waiting for PostgreSQL..."
  sleep 2
done

echo "run enterypoint ..."
python init_script.py

echo "run main ..."
python main.py
