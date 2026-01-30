# Deribit Price Monitor

FastAPI приложение для мониторинга цен криптовалют с биржи Deribit. Проект реализует клиент для получения цен, REST API для доступа к данным и периодические задачи для автоматического сбора информации.

## 🎯 Соответствие Техническому Заданию

### ✅ Обязательные требования (выполнены полностью):
1. **Клиент для Deribit** - получает цены BTC/USD и ETH/USD каждую минуту
2. **FastAPI с 3 GET-методами**:
   - `GET /api/prices?ticker=...` - все сохраненные данные по валюте
   - `GET /api/latest-price?ticker=...` - последняя цена валюты
   - `GET /api/price-by-date?ticker=...&date=...` - цена с фильтром по дате
3. **PostgreSQL** - основная база данных
4. **Celery** - для периодических задач
5. **README с инструкцией** - этот документ

### ✅ Необязательные требования (все выполнены):
1. **Unit-тесты** - 8 тестов покрывают основные функции
2. **2 контейнера** - приложение и БД развернуты в Docker
3. **aiohttp в клиенте** - асинхронные HTTP-запросы к API Deribit

## 🚀 Быстрый старт

### Предварительные требования
- Docker и Docker Compose
- Git

### Установка и запуск
```bash
# 1. Клонировать репозиторий
git clone https://github.com/GeraHelloMoto/deribit_proj.git
cd deribit_proj

# 2. Запустить контейнеры
docker-compose up -d


#3 Запустить Celery (в отдельном терминале или добавить в docker-compose)
docker-compose exec -d app celery -A src.tasks.price_fetcher.app worker --loglevel=info
docker-compose exec -d app celery -A src.tasks.price_fetcher.app beat --loglevel=info


# 4. Проверить статус
docker-compose ps

# 5. Проверить тесты
docker-compose exec app pytest tests/ -v

