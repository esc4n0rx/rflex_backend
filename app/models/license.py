"""
Modelo de Licença.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Enum as SQLEnum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.models.base import BaseModel


class LicenseStatus(str, enum.Enum):
    """Status possíveis de uma licença."""
    INACTIVE = "inactive"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    EXPIRED = "expired"


class License(BaseModel):
    """
    Licença de uso do RFlex.

    Uma licença está vinculada a uma empresa e um plano.
    Possui um código único de 32 caracteres usado para ativação.

    Atributos:
        id: Identificador único
        code: Código único de 32 caracteres (alfanumérico)
        company_id: ID da empresa proprietária
        plan_id: ID do plano contratado
        status: Status da licença (inactive/active/suspended/expired)
        expires_at: Data de expiração da licença
        notes: Observações
    """
    __tablename__ = "licenses"

    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        comment="ID único da licença"
    )
    code = Column(
        String(32),
        unique=True,
        index=True,
        nullable=False,
        comment="Código único de 32 caracteres"
    )
    company_id = Column(
        String(36),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        comment="ID da empresa proprietária"
    )
    plan_id = Column(
        String(36),
        ForeignKey("plans.id", ondelete="RESTRICT"),
        nullable=False,
        comment="ID do plano contratado"
    )
    status = Column(
        SQLEnum(LicenseStatus),
        default=LicenseStatus.INACTIVE,
        nullable=False,
        comment="Status da licença"
    )
    expires_at = Column(
        DateTime,
        nullable=False,
        comment="Data de expiração da licença"
    )
    notes = Column(
        Text,
        nullable=True,
        comment="Observações sobre a licença"
    )

    # Relacionamentos
    company = relationship(
        "Company",
        back_populates="licenses",
        lazy="selectin"
    )
    plan = relationship(
        "Plan",
        back_populates="licenses",
        lazy="selectin"
    )
    device_activations = relationship(
        "DeviceActivation",
        back_populates="license",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    def is_valid(self) -> bool:
        """
        Verifica se a licença está válida.

        Returns:
            True se status é ACTIVE e não está expirada
        """
        if self.status != LicenseStatus.ACTIVE:
            return False
        if self.expires_at < datetime.utcnow():
            return False
        return True

    def is_expired(self) -> bool:
        """
        Verifica se a licença está expirada.

        Returns:
            True se expires_at < agora
        """
        return self.expires_at < datetime.utcnow()

    def get_active_devices_count(self) -> int:
        """
        Retorna o número de dispositivos ativos nesta licença.

        Returns:
            Número de ativações ativas
        """
        return len([d for d in self.device_activations if d.is_active])
