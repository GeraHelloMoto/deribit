from fastapi import APIRouter, Query, HTTPException
from typing import List
from datetime import datetime
from src.database import crud  # Импортируем модуль, а не функции напрямую
from src.database.models import engine
from sqlalchemy import text

router = APIRouter()

# ============ HEALTH CHECK ============
@router.get("/health")
async def health_check():
    """Проверка здоровья API и базы данных"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
        
        return {
            "status": "healthy",
            "service": "Deribit Price Monitor",
            "database": "connected",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# ============ ALL PRICES ============
@router.get("/prices")
async def get_all_prices(ticker: str = Query(...)):
    """Получение всех сохраненных данных по указанной валюте"""
    if ticker not in ["btc_usd", "eth_usd"]:
        raise HTTPException(status_code=400, detail="Неподдерживаемый тикер. Используйте btc_usd или eth_usd")
    
    prices = crud.get_prices_by_ticker(ticker)  # Используем crud. для доступа
    if not prices:
        raise HTTPException(status_code=404, detail="Данные не найдены")
    
    return prices

# ============ LATEST PRICE ============
@router.get("/latest-price")
async def get_latest_price_endpoint(ticker: str = Query(...)):  # Переименовываем функцию
    """Получение последней цены валюты"""
    if ticker not in ["btc_usd", "eth_usd"]:
        raise HTTPException(status_code=400, detail="Неподдерживаемый тикер. Используйте btc_usd или eth_usd")
    
    price_data = crud.get_latest_price(ticker)  # Используем crud. для доступа
    if not price_data:
        raise HTTPException(status_code=404, detail="Данные не найдены")
    
    return price_data

# ============ PRICE BY DATE ============
@router.get("/price-by-date")
async def get_price_by_date(
    ticker: str = Query(...),
    date_from: str = Query(...),
    date_to: str = Query(...)
):
    """Получение цены валюты с фильтром по дате"""
    if ticker not in ["btc_usd", "eth_usd"]:
        raise HTTPException(status_code=400, detail="Неподдерживаемый тикер")
    
    try:
        from_dt = datetime.strptime(date_from, "%Y-%m-%d")
        to_dt = datetime.strptime(date_to, "%Y-%m-%d")
        
        from_dt = from_dt.replace(hour=0, minute=0, second=0)
        to_dt = to_dt.replace(hour=23, minute=59, second=59)
        
        date_from_ts = int(from_dt.timestamp())
        date_to_ts = int(to_dt.timestamp())
    except ValueError:
        raise HTTPException(status_code=400, detail="Неверный формат даты. Используйте YYYY-MM-DD")
    
    prices = crud.get_prices_by_date_range(ticker, date_from_ts, date_to_ts)
    if not prices:
        raise HTTPException(status_code=404, detail="Данные не найдены для указанного периода")
    
    return prices
