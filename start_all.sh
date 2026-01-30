#!/bin/bash
# start_all.sh - запуск всех сервисов

echo "🚀 Запуск всех сервисов..."

# Ждем БД
sleep 10

# Запускаем Celery worker в фоне
echo "Запуск Celery worker..."
celery -A src.tasks.price_fetcher.app worker --loglevel=info --detach

# Запускаем Celery beat в фоне  
echo "Запуск Celery beat..."
celery -A src.tasks.price_fetcher.app beat --loglevel=info --detach

# Запускаем FastAPI (основной процесс)
echo "Запуск FastAPI..."
uvicorn src.main:app --host 0.0.0.0 --port 8000
