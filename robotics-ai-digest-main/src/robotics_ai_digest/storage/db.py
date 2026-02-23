from __future__ import annotations

from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from .models import Base


def _build_sqlite_url(db_path: str) -> str:
    if db_path == ":memory:":
        return "sqlite:///:memory:"
    # Replace backslashes to build a valid SQLite URL on Windows.
    return f"sqlite:///{db_path.replace(chr(92), '/')}"


def init_db(db_path: str) -> sessionmaker[Session]:
    if db_path != ":memory:":
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    engine: Engine = create_engine(_build_sqlite_url(db_path), future=True)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

