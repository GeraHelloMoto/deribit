import pytest
from datetime import datetime
from decimal import Decimal

def test_health_endpoint(client):
    """Тест эндпоинта /api/health"""
    response = client.get("/api/health")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "status" in data
    assert "database" in data
    assert "timestamp" in data
    print("✅ Health endpoint works")

def test_get_prices_endpoint(client):
    """Тест эндпоинта /api/prices"""
    response = client.get("/api/prices?ticker=btc_usd")
    
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2  # Должно быть 2 записи BTC
    
    for item in data:
        assert "ticker" in item
        assert "price" in item
        assert "timestamp" in item
        assert item["ticker"] == "btc_usd"
    
    print(f"✅ Получено {len(data)} записей BTC")

def test_latest_price_endpoint(client):
    """Тест эндпоинта /api/latest-price"""
    response = client.get("/api/latest-price?ticker=btc_usd")
    
    assert response.status_code == 200
    
    data = response.json()
    assert "ticker" in data
    assert "price" in data
    assert "timestamp" in data
    assert data["ticker"] == "btc_usd"
    
    print(f"✅ Последняя цена BTC: ${data['price']}")

def test_price_by_date_endpoint(client):
    """Тест эндпоинта /api/price-by-date"""
    today = datetime.now().strftime("%Y-%m-%d")
    response = client.get(f"/api/price-by-date?ticker=btc_usd&date={today}")
    
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, list)
    
    print(f"✅ Получено {len(data)} записей за {today}")

def test_tickers_endpoint(client):
    """Тест эндпоинта /api/tickers"""
    response = client.get("/api/tickers")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "tickers" in data
    assert isinstance(data["tickers"], list)
    
    tickers = data["tickers"]
    assert "btc_usd" in tickers, f"Expected btc_usd in {tickers}"
    assert "eth_usd" in tickers, f"Expected eth_usd in {tickers}"
    
    print(f"✅ Найдены тикеры: {tickers}")

def test_api_requires_ticker_parameter(client):
    """Тест что API методы требуют параметр ticker"""
    endpoints = ["/api/prices", "/api/latest-price"]
    
    for endpoint in endpoints:
        response = client.get(endpoint)
        assert response.status_code == 422, f"Endpoint {endpoint} should require ticker parameter"
        print(f"✅ {endpoint} requires ticker parameter")

def test_api_returns_unix_timestamp(client):
    """Тест что API возвращает UNIX timestamp"""
    response = client.get("/api/prices?ticker=btc_usd")
    
    assert response.status_code == 200
    data = response.json()
    
    for item in data:
        timestamp = item.get("timestamp")
        assert isinstance(timestamp, int), f"Timestamp должен быть int, получили {type(timestamp)}"
        assert timestamp > 1262304000, f"Нереалистичный timestamp: {timestamp}"
    
    print("✅ Все записи имеют UNIX timestamp")

def test_data_structure(db_session):
    """Тест структуры данных (соответствие ТЗ)"""
    from src.database.models import PriceData
    
    test_price = PriceData(
        ticker="test_btc_usd",
        price=Decimal("12345.67"),
        timestamp=1234567890
    )
    
    db_session.add(test_price)
    db_session.commit()
    db_session.refresh(test_price)
    
    assert isinstance(test_price.id, int)
    assert isinstance(test_price.ticker, str)
    assert isinstance(test_price.price, Decimal)
    assert isinstance(test_price.timestamp, int)
    assert test_price.timestamp > 1000000000
    
    print(f"✅ Структура данных корректна")
