#!/bin/bash
export PYTHONPATH=/app

# لیست فولدرهای تست
folders=("tests/models_tests" "tests/services_tests")

for folder in "${folders[@]}"; do
    echo "==================== Running tests in $folder ===================="
    pytest "$folder" -v
    echo ""
done

exec "$@"
