from collections.abc import Generator
import os
import time

from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from app.core.config import DATABASE_URL

Base = declarative_base()

_engine = None
SessionLocal = sessionmaker(autocommit=False, autoflush=False)


def _create_engine():
    connect_args = {}
    if DATABASE_URL.startswith("postgresql"):
        connect_args["connect_timeout"] = int(os.getenv("DB_CONNECT_TIMEOUT", "5"))

    return create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=int(os.getenv("DB_POOL_RECYCLE", "300")),
        pool_size=int(os.getenv("DB_POOL_SIZE", "5")),
        max_overflow=int(os.getenv("DB_MAX_OVERFLOW", "2")),
        pool_timeout=int(os.getenv("DB_POOL_TIMEOUT", "30")),
        connect_args=connect_args,
    )


def get_engine():
    global _engine
    if _engine is None:
        _engine = _create_engine()
        SessionLocal.configure(bind=_engine)
    return _engine


def check_database_connection(retries: int = 3, delay: float = 0.75) -> None:
    last_error = None
    for attempt in range(1, retries + 1):
        try:
            engine = get_engine()
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            return
        except SQLAlchemyError as exc:
            last_error = exc
            if attempt < retries:
                time.sleep(delay)
    if last_error is not None:
        raise last_error


def get_db() -> Generator[Session, None, None]:
    get_engine()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
