"""
Modelo de Empresa (Cliente).
"""
import uuid
from sqlalchemy import Column, String, Text, Boolean
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Company(BaseModel):
    """
    Empresa cliente que utiliza o RFlex.

    Atributos:
        id: Identificador único (UUID)
        trading_name: Nome fantasia
        legal_name: Razão social
        cnpj: CNPJ da empresa
        email: Email principal de contato
        phone: Telefone de contato
        address: Endereço completo
        is_active: Se a empresa está ativa
        notes: Observações adicionais
    """
    __tablename__ = "companies"

    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        comment="ID único da empresa (UUID)"
    )
    trading_name = Column(
        String(255),
        nullable=False,
        comment="Nome fantasia da empresa"
    )
    legal_name = Column(
        String(255),
        nullable=False,
        comment="Razão social da empresa"
    )
    cnpj = Column(
        String(20),
        unique=True,
        index=True,
        nullable=True,
        comment="CNPJ da empresa"
    )
    email = Column(
        String(255),
        nullable=False,
        comment="Email principal de contato"
    )
    phone = Column(
        String(20),
        nullable=True,
        comment="Telefone de contato"
    )
    address = Column(
        Text,
        nullable=True,
        comment="Endereço completo"
    )
    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="Se a empresa está ativa"
    )
    notes = Column(
        Text,
        nullable=True,
        comment="Observações adicionais"
    )

    # Relacionamentos
    licenses = relationship(
        "License",
        back_populates="company",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
