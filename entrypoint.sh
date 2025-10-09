#!/bin/bash

echo "⏳ منتظر شدن برای آماده شدن دیتابیس..."
until pg_isready -h "$PGHOST" -p "5432" >/dev/null 2>&1; do
  echo "Waiting for PostgreSQL..."
  sleep 2
done

echo "✅ اجرای فایل اولیه (مثلاً ایجاد جداول)..."
python init_script.py

echo "🚀 اجرای برنامه اصلی..."
python main.py
