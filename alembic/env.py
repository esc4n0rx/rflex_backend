"""
Configuração do ambiente Alembic.
"""
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import sys
from pathlib import Path

# Adiciona diretório raiz ao path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.config import settings
from app.core.database import Base
from app.models import *  # Importa todos os modelos

# Configuração Alembic
config = context.config

# Interpreta config file para Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadata para autogenerate
target_metadata = Base.metadata

# Override database URL com variável de ambiente
config.set_main_option("sqlalchemy.url", settings.database_url)


def run_migrations_offline() -> None:
    """
    Roda migrations em modo 'offline'.

    Isso configura o contexto com apenas uma URL
    e não uma Engine, embora uma Engine seja aceitável
    aqui também. Ao pular a criação da Engine, nem mesmo
    precisamos de um DBAPI disponível.

    Calls to context.execute() aqui emitem a string
    dada para a output script.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Roda migrations em modo 'online'.

    Neste cenário precisamos criar uma Engine
    e associar uma conexão com o contexto.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
