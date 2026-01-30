import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from decimal import Decimal
import time

from src.main import app
from src.database.models import Base, PriceData
from src.database.database import get_db

# Тестовая БД в памяти
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

@pytest.fixture(scope="session")
def test_db_engine():
    """Создаём таблицы один раз для всех тестов."""
    Base.metadata.create_all(bind=test_engine)
    yield test_engine
    Base.metadata.drop_all(bind=test_engine)

@pytest.fixture(scope="function")
def db_session(test_db_engine):
    """Создаём новую сессию БД с тестовыми данными для каждого теста."""
    connection = test_db_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    # Тестовые данные
    test_prices = [
        PriceData(ticker="btc_usd", price=Decimal("50000.50"), timestamp=int(time.time()) - 3600),
        PriceData(ticker="eth_usd", price=Decimal("3000.75"), timestamp=int(time.time()) - 1800),
        PriceData(ticker="btc_usd", price=Decimal("50100.25"), timestamp=int(time.time())),
    ]
    for price in test_prices:
        session.add(price)
    session.commit()

    yield session

    # Очистка
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope="function")
def client(db_session):
    """Тестовый клиент API."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
