from __future__ import annotations

from collections.abc import Generator
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from controldiff.config import settings
from controldiff.db.base import Base


def _sqlite_path_from_url(url: str) -> Path | None:
    sqlite_prefixes = ("sqlite+pysqlite:///", "sqlite:///")
    for prefix in sqlite_prefixes:
        if url.startswith(prefix):
            return Path(url.removeprefix(prefix))
    return None


settings.ensure_runtime_directories()
resolved_database_url = settings.resolved_database_url

sqlite_path = _sqlite_path_from_url(resolved_database_url)
if sqlite_path is not None:
    sqlite_path.parent.mkdir(parents=True, exist_ok=True)

connect_args = {"check_same_thread": False} if sqlite_path is not None else {}

engine = create_engine(
    resolved_database_url,
    future=True,
    connect_args=connect_args,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    future=True,
)


def init_db() -> None:
    from controldiff.domain import models  # noqa: F401

    Base.metadata.create_all(bind=engine)


def get_session() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
