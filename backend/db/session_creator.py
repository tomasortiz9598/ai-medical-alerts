import os
import sys
from typing import Any

from db.models.base import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool
from utils.settings import AppSettings


def get_db_uri() -> str:
    _settings = AppSettings()
    if "pytest" in sys.modules:
        return "sqlite+pysqlite:///:memory:"
    return f"postgresql+psycopg2://{_settings.PGUSER}:{_settings.PGPASSWORD}@{_settings.PGHOST}:{_settings.PGPORT}/{_settings.PGDATABASE}"


def get_db_session(
    postgres_url: str = get_db_uri(),
    echo: bool = False,
    pool_size: int | None = None,
    create_metadata: bool = False,
    **kwargs: Any,
) -> Session:
    os.environ["SQLALCHEMY_WARN_20"] = "true"
    is_sqlite = postgres_url.startswith("sqlite")
    if is_sqlite:
        kwargs.setdefault("connect_args", {})
        kwargs["connect_args"].setdefault("check_same_thread", False)
        kwargs.setdefault("poolclass", StaticPool)
        pool_size = None
    if pool_size:
        kwargs["pool_size"] = pool_size
        kwargs["max_overflow"] = 20
        kwargs["pool_recycle"] = 1800
        kwargs["pool_timeout"] = 30

    engine = create_engine(
        postgres_url, pool_pre_ping=not is_sqlite, future=True, echo=echo, **kwargs
    )
    if create_metadata:
        Base.metadata.create_all(bind=engine)
    session_maker = sessionmaker(
        bind=engine, autoflush=False, autocommit=False, future=True
    )
    return session_maker()
