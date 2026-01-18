"""
Modelo de Log de Validação.
"""
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum
import uuid

from app.models.base import BaseModel


class ValidationStatus(str, enum.Enum):
    """Status possíveis de uma validação."""
    SUCCESS = "success"
    FAILED = "failed"
    GRACE_PERIOD = "grace_period"


class ValidationLog(BaseModel):
    """
    Log de tentativas de validação de licença.

    Cada vez que um coletor valida sua licença, um registro é criado.
    Útil para auditoria, troubleshooting e métricas de uso.

    Atributos:
        id: Identificador único
        device_activation_id: ID da ativação do dispositivo
        status: Status da validação (success/failed/grace_period)
        ip_address: Endereço IP da requisição
        user_agent: User agent do app
        is_offline: Se estava em modo offline
        error_message: Mensagem de erro (se falhou)
        validated_at: Data/hora da validação
        response_time_ms: Tempo de resposta da API (em ms)
    """
    __tablename__ = "validation_logs"

    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        comment="ID único do log"
    )
    device_activation_id = Column(
        String(36),
        ForeignKey("device_activations.id", ondelete="CASCADE"),
        nullable=False,
        comment="ID da ativação do dispositivo"
    )
    status = Column(
        SQLEnum(ValidationStatus),
        nullable=False,
        comment="Status da validação"
    )
    ip_address = Column(
        String(45),
        nullable=True,
        comment="Endereço IP da requisição (IPv4 ou IPv6)"
    )
    user_agent = Column(
        String(500),
        nullable=True,
        comment="User agent do app"
    )
    is_offline = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="Se estava em modo offline"
    )
    error_message = Column(
        Text,
        nullable=True,
        comment="Mensagem de erro (se falhou)"
    )
    validated_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        comment="Data/hora da validação"
    )
    response_time_ms = Column(
        String(20),
        nullable=True,
        comment="Tempo de resposta da API (ms)"
    )

    # Relacionamentos
    device_activation = relationship(
        "DeviceActivation",
        back_populates="validation_logs",
        lazy="selectin"
    )
