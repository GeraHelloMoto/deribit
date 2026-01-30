import asyncio
from celery import Celery
import logging
from src.client.deribit_client import DeribitClient
from src.database.crud import save_price_data
from src.database.database import SessionLocal
import os

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Конфигурация Celery с SQLite брокером (вместо Redis)
broker_url = os.getenv('CELERY_BROKER_URL', 'sqla+sqlite:///celery.db')
result_backend = os.getenv('CELERY_RESULT_BACKEND', 'db+sqlite:///results.db')

app = Celery('price_fetcher')
app.conf.broker_url = broker_url
app.conf.result_backend = result_backend
app.conf.broker_connection_retry_on_startup = True

# Расписание задач
app.conf.beat_schedule = {
    'fetch-prices-every-minute': {
        'task': 'src.tasks.price_fetcher.fetch_prices',
        'schedule': 60.0,  # каждые 60 секунд
    },
}

@app.task
def fetch_prices():
    """Задача для получения цен с Deribit и сохранения в БД"""
    logger.info("🚀 Запуск задачи fetch_prices...")
    
    try:
        # Получаем цены
        prices = asyncio.run(_async_fetch_prices())
        
        if not prices:
            logger.warning("⚠️ Не получено ни одной цены")
            return {"status": "no_prices"}
        
        # Фильтруем None значения
        valid_prices = {k: v for k, v in prices.items() if v is not None}
        
        if not valid_prices:
            logger.warning("⚠️ Все полученные цены были None")
            return {"status": "all_prices_none"}
        
        # Сохраняем в БД
        db = SessionLocal()
        saved_count = 0
        try:
            for ticker, price_data in valid_prices.items():
                save_price_data(
                    db=db,
                    ticker=ticker,
                    price=price_data["price"],
                    timestamp=price_data["timestamp"]
                )
                saved_count += 1
                logger.info(f"✅ Сохранена цена {ticker}: ${price_data['price']}")
            
            db.commit()
            logger.info(f"🎉 Успешно сохранено {saved_count} из {len(prices)} цен")
            
        except Exception as e:
            db.rollback()
            logger.error(f"❌ Ошибка сохранения в БД: {e}")
            raise
        finally:
            db.close()
            
        return {"status": "success", "saved": saved_count, "total": len(prices)}
        
    except Exception as e:
        logger.error(f"💥 Критическая ошибка в задаче fetch_prices: {e}")
        return {"status": "error", "message": str(e)}

async def _async_fetch_prices():
    """Асинхронное получение всех цен"""
    tickers = ["btc_usd", "eth_usd"]
    logger.info(f"🔄 Запрос цен для тикеров: {tickers}")
    
    try:
        async with DeribitClient() as client:
            prices = await client.get_multiple_prices(tickers)
            logger.info(f"📊 Получены цены: { {k: v is not None for k, v in prices.items()} }")
            return prices
    except Exception as e:
        logger.error(f"❌ Ошибка при работе с клиентом: {e}")
        return {}

if __name__ == "__main__":
    # Для ручного тестирования
    result = fetch_prices()
    print(f"Результат: {result}")
