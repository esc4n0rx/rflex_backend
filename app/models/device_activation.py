"""
Modelo de Ativação de Dispositivo (Coletor).
"""
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, Text, JSON
from sqlalchemy.orm import relationship
import uuid

from app.models.base import BaseModel


class DeviceActivation(BaseModel):
    """
    Representa a ativação de um coletor (dispositivo) em uma licença.

    Cada coletor é identificado por um device_id único gerado pelo app RFlex.
    Um dispositivo pode ser revogado e reativado.

    Atributos:
        id: Identificador único
        license_id: ID da licença utilizada
        device_id: UUID do dispositivo (gerado pelo app)
        device_name: Nome/identificação do coletor
        device_manufacturer: Fabricante do coletor
        device_model: Modelo do coletor
        android_version: Versão do Android
        app_version: Versão do app RFlex
        hardware_info: Informações adicionais de hardware (JSON)
        activated_at: Data/hora da ativação
        last_validated_at: Data/hora da última validação bem-sucedida
        is_active: Se a ativação está ativa (não revogada)
        is_revoked: Se foi explicitamente revogada
        revoked_at: Data/hora da revogação
        revoke_reason: Motivo da revogação
    """
    __tablename__ = "device_activations"

    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        comment="ID único da ativação"
    )
    license_id = Column(
        String(36),
        ForeignKey("licenses.id", ondelete="CASCADE"),
        nullable=False,
        comment="ID da licença utilizada"
    )
    device_id = Column(
        String(36),
        unique=True,
        index=True,
        nullable=False,
        comment="UUID do dispositivo (gerado pelo app)"
    )
    device_name = Column(
        String(255),
        nullable=True,
        comment="Nome/identificação do coletor"
    )
    device_manufacturer = Column(
        String(100),
        nullable=True,
        comment="Fabricante do coletor"
    )
    device_model = Column(
        String(100),
        nullable=True,
        comment="Modelo do coletor"
    )
    android_version = Column(
        String(20),
        nullable=True,
        comment="Versão do Android"
    )
    app_version = Column(
        String(20),
        nullable=True,
        comment="Versão do app RFlex"
    )
    hardware_info = Column(
        JSON,
        nullable=True,
        comment="Informações adicionais de hardware"
    )
    activated_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        comment="Data/hora da ativação"
    )
    last_validated_at = Column(
        DateTime,
        nullable=True,
        comment="Data/hora da última validação bem-sucedida"
    )
    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="Se a ativação está ativa"
    )
    is_revoked = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="Se foi explicitamente revogada"
    )
    revoked_at = Column(
        DateTime,
        nullable=True,
        comment="Data/hora da revogação"
    )
    revoke_reason = Column(
        Text,
        nullable=True,
        comment="Motivo da revogação"
    )

    # Relacionamentos
    license = relationship(
        "License",
        back_populates="device_activations",
        lazy="selectin"
    )
    validation_logs = relationship(
        "ValidationLog",
        back_populates="device_activation",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    def revoke(self, reason: str = None) -> None:
        """
        Revoga a ativação deste dispositivo.

        Args:
            reason: Motivo da revogação (opcional)
        """
        self.is_active = False
        self.is_revoked = True
        self.revoked_at = datetime.utcnow()
        self.revoke_reason = reason

    def reactivate(self) -> None:
        """
        Reativa a ativação deste dispositivo.
        """
        self.is_active = True
        self.is_revoked = False
        self.revoked_at = None
        self.revoke_reason = None

    def update_validation(self) -> None:
        """
        Atualiza o timestamp da última validação bem-sucedida.
        """
        self.last_validated_at = datetime.utcnow()
