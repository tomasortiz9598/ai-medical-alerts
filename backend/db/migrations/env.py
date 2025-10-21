import os
import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import engine_from_config, pool

# Ensure the backend package is importable when running Alembic commands
ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from db.models.base import Base
from db.models.event import Event  # noqa: F401
from db.models.event_type import EventType  # noqa: F401
from db.models.medical_record import MedicalRecord  # noqa: F401
from db.session_creator import get_db_uri

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def _resolve_database_url() -> str:
    url = os.getenv("DATABASE_URL")
    if url:
        return url
    try:
        return get_db_uri()
    except Exception:
        # Fallback to assembling from discrete environment variables or config
        db_host = os.getenv("DB_HOST", os.getenv("PGHOST", "localhost"))
        db_port = os.getenv("DB_PORT", os.getenv("PGPORT", "5432"))
        db_name = os.getenv("DB_NAME", os.getenv("PGDATABASE", "medical_alerts"))
        db_user = os.getenv("DB_USER", os.getenv("PGUSER", "postgres"))
        db_password = os.getenv("DB_PASSWORD", os.getenv("PGPASSWORD", ""))
        if not any([db_host, db_name, db_user]):
            return context.config.get_main_option("sqlalchemy.url")

        if db_password:
            return f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        return f"postgresql://{db_user}@{db_host}:{db_port}/{db_name}"


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    # Get URL from environment variables or fallback to config
    url = _resolve_database_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    # Get configuration from environment or config file
    configuration = config.get_section(config.config_ini_section, {})

    # Override with environment variables or application settings if set
    configuration["sqlalchemy.url"] = _resolve_database_url()

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
