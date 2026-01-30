from sqlalchemy import create_engine, Column, Integer, String, DECIMAL, BigInteger, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# Используем psycopg3 вместо psycopg2
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg://postgres:password@localhost:5432/deribit_db")

engine = create_engine(DATABASE_URL)
Base = declarative_base()

class PriceData(Base):
    __tablename__ = "price_data"
    
    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String(20), nullable=False, index=True)
    price = Column(DECIMAL(15, 2), nullable=False)
    timestamp = Column(BigInteger, nullable=False, index=True)  # UNIX timestamp как в ТЗ
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<PriceData(ticker='{self.ticker}', price={self.price}, timestamp={self.timestamp})>"

# Создаем SessionLocal для работы с БД
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
