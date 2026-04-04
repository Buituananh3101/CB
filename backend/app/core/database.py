from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import os
from app.core.config import settings

# Lấy DATABASE_URL từ settings. Thay sqlite thành postgresql thông qua .env
# Mặc định (khi code cũ) là "sqlite:///./mathbot.db"
# Với Postgres, cấu trúc sẽ là "postgresql://user:password@localhost/dbname"
DATABASE_URL = os.getenv("DATABASE_URL", settings.DATABASE_URL)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
