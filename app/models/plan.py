"""
Modelo de Plano de Licenciamento.
"""
import uuid
from sqlalchemy import Column, String, Integer, Float, Text, Boolean
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Plan(BaseModel):
    """
    Plano de licenciamento disponível para empresas.

    Planos disponíveis:
    - Starter: Até 5 coletores
    - Pro: Até 20 coletores
    - Enterprise: Coletores ilimitados

    Atributos:
        id: Identificador único
        name: Nome do plano
        max_devices: Número máximo de coletores (-1 para ilimitado)
        price_per_device: Preço por coletor/mês
        description: Descrição do plano
        features: Lista de recursos em formato JSON
        is_active: Se o plano está disponível
        is_enterprise: Se é plano enterprise (personalizado)
    """
    __tablename__ = "plans"

    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        comment="ID único do plano"
    )
    name = Column(
        String(100),
        unique=True,
        nullable=False,
        comment="Nome do plano (ex: RFlex Starter)"
    )
    max_devices = Column(
        Integer,
        nullable=False,
        comment="Número máximo de coletores (-1 para ilimitado)"
    )
    price_per_device = Column(
        Float,
        nullable=False,
        comment="Preço por coletor/mês (R$)"
    )
    description = Column(
        Text,
        nullable=True,
        comment="Descrição do plano"
    )
    features = Column(
        Text,
        nullable=True,
        comment="Recursos do plano (JSON string)"
    )
    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="Se o plano está disponível para novas licenças"
    )
    is_enterprise = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="Se é plano enterprise (personalizado)"
    )

    # Relacionamentos
    licenses = relationship(
        "License",
        back_populates="plan",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
