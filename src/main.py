from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
from datetime import datetime
import os
from contextlib import asynccontextmanager

from src.database.models import PriceData, Base, engine
from src.database.database import get_db, SessionLocal
from src.database.crud import (
    get_all_prices,
    get_latest_price,
    get_prices_by_date,
    save_price_data
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Запуск FastAPI приложения...")
    try:
        # Проверяем подключение к БД
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        
        # Создаем таблицы если их нет
        Base.metadata.create_all(bind=engine)
        print("✅ Таблицы базы данных созданы/проверены")
    except Exception as e:
        print(f"⚠️  Предупреждение: не удалось подключиться к БД при старте: {e}")
        print("Приложение запустится, но некоторые функции могут не работать")
    
    yield
    
    # Shutdown
    print("Приложение завершает работу")

app = FastAPI(title="Deribit Price Monitor", version="1.0.0", lifespan=lifespan)

@app.get("/api/health")
async def health_check(db: Session = Depends(get_db)):
    """Проверка здоровья приложения"""
    try:
        # Проверяем подключение к БД
        db.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "database": "connected",
            "database_type": "PostgreSQL",
            "timestamp": datetime.now().isoformat(),
            "message": "Все системы работают нормально"
        }
    except Exception as e:
        return {
            "status": "degraded",
            "database": "disconnected",
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
            "message": "API работает, но БД недоступна"
        }

@app.get("/api/prices")
async def get_prices(
    ticker: str = Query(..., description="Тикер валюты (btc_usd или eth_usd)"),
    limit: int = Query(100, description="Количество записей"),
    db: Session = Depends(get_db)
):
    """Получение всех сохраненных данных по указанной валюте (Требование ТЗ)"""
    prices = get_all_prices(db, ticker=ticker, limit=limit)
    
    return [
        {
            "id": price.id,
            "ticker": price.ticker,
            "price": float(price.price),
            "timestamp": price.timestamp,
            "datetime": datetime.fromtimestamp(price.timestamp).isoformat(),
            "created_at": price.created_at.isoformat()
        }
        for price in prices
    ]

@app.get("/api/latest-price")
async def get_latest(
    ticker: str = Query(..., description="Тикер валюты (btc_usd или eth_usd)"),
    db: Session = Depends(get_db)
):
    """Получение последней цены валюты (Требование ТЗ)"""
    price = get_latest_price(db, ticker=ticker)
    
    if not price:
        raise HTTPException(status_code=404, detail=f"No data found for ticker: {ticker}")
    
    return {
        "ticker": price.ticker,
        "price": float(price.price),
        "timestamp": price.timestamp,
        "datetime": datetime.fromtimestamp(price.timestamp).isoformat(),
        "created_at": price.created_at.isoformat()
    }

@app.get("/api/price-by-date")
async def get_price_by_date(
    ticker: str = Query(..., description="Тикер валюты (btc_usd или eth_usd)"),
    date: str = Query(..., description="Дата в формате YYYY-MM-DD"),
    db: Session = Depends(get_db)
):
    """Получение цены валюты с фильтром по дате (Требование ТЗ)"""
    try:
        target_date = datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    prices = get_prices_by_date(db, ticker=ticker, date=target_date)
    
    return [
        {
            "id": price.id,
            "ticker": price.ticker,
            "price": float(price.price),
            "timestamp": price.timestamp,
            "datetime": datetime.fromtimestamp(price.timestamp).isoformat(),
            "created_at": price.created_at.isoformat()
        }
        for price in prices
    ]

@app.get("/api/tickers")
async def get_tickers(db: Session = Depends(get_db)):
    """Получение списка доступных тикеров"""
    try:
        tickers = db.query(PriceData.ticker).distinct().all()
        return {"tickers": [ticker[0] for ticker in tickers]}
    except Exception as e:
        # Если таблицы еще нет или нет данных
        return {"tickers": [], "message": "No data yet", "error": str(e)}

# Новый эндпоинт для добавления тестовых данных
@app.post("/api/test-data")
async def add_test_data(db: Session = Depends(get_db)):
    """Добавление тестовых данных для демонстрации"""
    import time
    
    test_data = [
        {"ticker": "btc_usd", "price": 45000.50, "timestamp": int(time.time() - 3600)},
        {"ticker": "btc_usd", "price": 45100.75, "timestamp": int(time.time() - 1800)},
        {"ticker": "btc_usd", "price": 45200.25, "timestamp": int(time.time())},
        {"ticker": "eth_usd", "price": 2500.30, "timestamp": int(time.time() - 3600)},
        {"ticker": "eth_usd", "price": 2510.45, "timestamp": int(time.time() - 1800)},
        {"ticker": "eth_usd", "price": 2520.60, "timestamp": int(time.time())},
    ]
    
    for data in test_data:
        save_price_data(db, data["ticker"], data["price"], data["timestamp"])
    
    return {"message": "Test data added", "count": len(test_data)}

@app.get("/api/stats")
async def get_stats(db: Session = Depends(get_db)):
    """Статистика базы данных"""
    from sqlalchemy import func
    
    try:
        total_records = db.query(func.count(PriceData.id)).scalar() or 0
        tickers_count = db.query(PriceData.ticker).distinct().count()
        
        return {
            "total_records": total_records,
            "unique_tickers": tickers_count,
            "database": "PostgreSQL",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"error": str(e), "message": "Database not ready yet"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
