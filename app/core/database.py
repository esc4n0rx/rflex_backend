"""
Configuração do banco de dados e sessão SQLAlchemy.
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

from app.core.config import settings

# Criar engine do banco de dados
# pool_pre_ping=True verifica se a conexão está válida antes de usar
# pool_recycle=3600 recicla conexões a cada 1 hora (evita timeouts do MySQL)
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=settings.environment == "development",  # Log queries em desenvolvimento
    pool_size=10,
    max_overflow=20
)

# Criar SessionLocal factory
# autocommit=False e autoflush=False são necessários para FastAPI
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base declarativa para os modelos
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency function para obter sessão do banco de dados.

    Garante que a sessão seja fechada após o uso,
    mesmo em caso de exceções.

    Yields:
        Session: Sessão SQLAlchemy ativa
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    Inicializa o banco de dados criando todas as tabelas.
    Use isso apenas em desenvolvimento. Em produção, use Alembic migrations.
    """
    from app.models import (
        AdminUser, Company, Plan, License,
        DeviceActivation, ValidationLog
    )
    Base.metadata.create_all(bind=engine)
