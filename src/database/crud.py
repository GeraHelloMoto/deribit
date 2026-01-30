from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime, timedelta
from .models import PriceData

def save_price_data(db: Session, ticker: str, price: float, timestamp: int):
    """Сохранение данных в БД"""
    db_price = PriceData(
        ticker=ticker,
        price=price,
        timestamp=timestamp
    )
    db.add(db_price)
    db.commit()
    db.refresh(db_price)
    return db_price

def get_all_prices(db: Session, ticker: str, limit: int = 1000):
    """Получение всех цен для тикера"""
    return db.query(PriceData)\
        .filter(PriceData.ticker == ticker)\
        .order_by(desc(PriceData.timestamp))\
        .limit(limit)\
        .all()

def get_latest_price(db: Session, ticker: str):
    """Получение последней цены для тикера"""
    return db.query(PriceData)\
        .filter(PriceData.ticker == ticker)\
        .order_by(desc(PriceData.timestamp))\
        .first()

def get_prices_by_date(db: Session, ticker: str, date: datetime):
    """Получение цен по дате"""
    start_timestamp = int(date.replace(hour=0, minute=0, second=0, microsecond=0).timestamp())
    end_timestamp = int((date + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0).timestamp())
    
    return db.query(PriceData)\
        .filter(PriceData.ticker == ticker)\
        .filter(PriceData.timestamp >= start_timestamp)\
        .filter(PriceData.timestamp < end_timestamp)\
        .order_by(desc(PriceData.timestamp))\
        .all()
