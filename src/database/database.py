from sqlalchemy.orm import Session
from .models import SessionLocal

def get_db() -> Session:
    """Генератор зависимости для FastAPI."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
