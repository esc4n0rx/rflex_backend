"""
Modelo base com campos comuns a todas as tabelas.
"""
from datetime import datetime
from sqlalchemy import Column, DateTime
from app.core.database import Base


class BaseModel(Base):
    """
    Modelo base com campos de timestamp.
    Todas as tabelas devem herdar deste modelo.
    """
    __abstract__ = True

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        comment="Data e hora de criação do registro"
    )
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
        comment="Data e hora da última atualização do registro"
    )
