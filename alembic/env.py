# db/alembic/env.py
from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context

from app.db.database import Base
from app.models import user, video
from sqlalchemy import create_engine
from app.core.config import settings
import os

# Ce fichier config d'Alembic accède au .ini fichier utilisé.
config = context.config

# Configure le logger
fileConfig(config.config_file_name)

# Remplace la URL de la base de données par celle utilisée dans l'application
# config.set_main_option("sqlalchemy.url", os.getenv("DATABASE_URL").replace("asyncpg", "psycopg2"))
config.set_main_option("sqlalchemy.url", os.getenv("DATABASE_URL").replace("asyncpg", "psycopg2"))

# Ciblez le metadata
target_metadata = Base.metadata


def run_migrations_offline():
    """Exécute les migrations en mode 'offline'."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url, target_metadata=target_metadata, literal_binds=True, dialect_opts={"paramstyle": "named"}
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Exécute les migrations en mode 'online'."""
    connectable = create_engine(config.get_main_option("sqlalchemy.url"))

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
