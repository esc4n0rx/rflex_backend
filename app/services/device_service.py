"""
Serviço de gerenciamento de dispositivos (coletores).
"""
from datetime import datetime, timedelta
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models import DeviceActivation, License, LicenseStatus, ValidationLog, ValidationStatus
from app.schemas import DeviceActivationRequest
from app.services.license_service import LicenseService
from app.core.security import create_device_token, verify_device_token
from app.core.config import settings


class DeviceService:
    """Serviço para operações de dispositivos."""

    @staticmethod
    def activate_device(
        db: Session,
        request: DeviceActivationRequest
    ) -> tuple[DeviceActivation, str]:
        """
        Ativa um dispositivo em uma licença.

        Args:
            db: Sessão do banco de dados
            request: Dados da ativação

        Returns:
            Tupla (DeviceActivation, token)

        Raises:
            ValueError: Se licença inválida, expirada ou sem vagas
        """
        # Busca licença pelo código
        license = db.query(License).filter(
            License.code == request.license_code
        ).first()

        if not license:
            raise ValueError("Licença não encontrada")

        # Verifica se está ativa
        if license.status != LicenseStatus.ACTIVE:
            raise ValueError(f"Licença não está ativa. Status: {license.status.value}")

        # Verifica se não expirou
        if license.is_expired:
            raise ValueError("Licença expirada")

        # Verifica disponibilidade
        if not LicenseService.check_availability(license):
            raise ValueError("Limite de dispositivos atingido")

        # Verifica se dispositivo já existe
        existing = db.query(DeviceActivation).filter(
            DeviceActivation.device_id == request.device_id
        ).first()

        if existing:
            # Se está na mesma licença e ativo, retorna token existente
            if existing.license_id == license.id and existing.is_active:
                token = create_device_token(request.device_id, license.id)
                return existing, token

            # Se está em outra licença ou revogado, reativa
            if existing.license_id != license.id:
                raise ValueError("Dispositivo já ativado em outra licença")

            # Reativa
            existing.reactivate()
            existing.device_name = request.device_name
            existing.device_manufacturer = request.device_manufacturer
            existing.device_model = request.device_model
            existing.android_version = request.android_version
            existing.app_version = request.app_version
            existing.hardware_info = request.hardware_info

            token = create_device_token(request.device_id, license.id)
            db.commit()
            db.refresh(existing)
            return existing, token

        # Cria nova ativação
        activation = DeviceActivation(
            license_id=license.id,
            device_id=request.device_id,
            device_name=request.device_name,
            device_manufacturer=request.device_manufacturer,
            device_model=request.device_model,
            android_version=request.android_version,
            app_version=request.app_version,
            hardware_info=request.hardware_info,
            activated_at=datetime.utcnow(),
            is_active=True
        )

        db.add(activation)
        db.commit()
        db.refresh(activation)

        # Cria token
        token = create_device_token(request.device_id, license.id)

        return activation, token

    @staticmethod
    def validate_device(
        db: Session,
        device_id: str,
        activation_token: str,
        is_offline: bool = False
    ) -> tuple[bool, str, Optional[License]]:
        """
        Valida se um dispositivo tem licença válida.

        Args:
            db: Sessão do banco de dados
            device_id: ID do dispositivo
            activation_token: Token de ativação
            is_offline: Se está em modo offline

        Returns:
            Tupla (válido, mensagem, licença)
        """
        # Verifica token
        token_data = verify_device_token(activation_token)
        if not token_data:
            return False, "Token de ativação inválido", None

        # Verifica device_id
        if token_data["device_id"] != device_id:
            return False, "Token não pertence a este dispositivo", None

        # Busca ativação
        activation = db.query(DeviceActivation).filter(
            DeviceActivation.device_id == device_id
        ).first()

        if not activation:
            return False, "Dispositivo não encontrado", None

        # Verifica se está ativo
        if not activation.is_active or activation.is_revoked:
            return False, "Dispositivo revogado", None

        # Busca licença
        license = db.query(License).filter(
            License.id == token_data["license_id"]
        ).first()

        if not license:
            return False, "Licença não encontrada", None

        # Verifica status da licença
        if license.status != LicenseStatus.ACTIVE:
            return False, f"Licença não está ativa. Status: {license.status.value}", license

        # Verifica expiração
        now = datetime.utcnow()
        grace_period_end = activation.last_validated_at + timedelta(hours=settings.grace_period_hours) if activation.last_validated_at else None

        if license.is_expired:
            # Verifica período de tolerância offline
            if is_offline and grace_period_end and grace_period_end > now:
                # Período de tolerância
                activation.update_validation()
                db.commit()
                return True, "Válido (período de tolerância offline)", license
            else:
                return False, "Licença expirada", license

        # Tudo OK - atualiza timestamp
        activation.update_validation()
        db.commit()

        return True, "Licença válida", license

    @staticmethod
    def get_device_activation(
        db: Session,
        activation_id: str
    ) -> Optional[DeviceActivation]:
        """Busca ativação por ID."""
        return db.query(DeviceActivation).filter(
            DeviceActivation.id == activation_id
        ).first()

    @staticmethod
    def get_device_by_device_id(
        db: Session,
        device_id: str
    ) -> Optional[DeviceActivation]:
        """Busca ativação por device_id."""
        return db.query(DeviceActivation).filter(
            DeviceActivation.device_id == device_id
        ).first()

    @staticmethod
    def list_devices(
        db: Session,
        license_id: Optional[str] = None,
        is_active: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[DeviceActivation], int]:
        """
        Lista dispositivos com filtros opcionais.

        Args:
            db: Sessão do banco de dados
            license_id: Filtrar por licença
            is_active: Filtrar por status ativo
            skip: Paginação
            limit: Limite de registros

        Returns:
            Tupla (lista de dispositivos, total)
        """
        query = db.query(DeviceActivation)

        if license_id:
            query = query.filter(DeviceActivation.license_id == license_id)
        if is_active is not None:
            query = query.filter(DeviceActivation.is_active == is_active)

        total = query.count()
        devices = query.order_by(
            DeviceActivation.created_at.desc()
        ).offset(skip).limit(limit).all()

        return devices, total

    @staticmethod
    def revoke_device(
        db: Session,
        activation: DeviceActivation,
        reason: Optional[str] = None
    ) -> DeviceActivation:
        """Revoga um dispositivo."""
        activation.revoke(reason)
        db.commit()
        db.refresh(activation)
        return activation

    @staticmethod
    def reactivate_device(
        db: Session,
        activation: DeviceActivation
    ) -> DeviceActivation:
        """Reativa um dispositivo revogado."""
        # Verifica disponibilidade na licença
        license = db.query(License).filter(
            License.id == activation.license_id
        ).first()

        if license and not LicenseService.check_availability(license):
            raise ValueError("Limite de dispositivos atingido")

        activation.reactivate()
        db.commit()
        db.refresh(activation)
        return activation

    @staticmethod
    def log_validation(
        db: Session,
        activation: DeviceActivation,
        status: ValidationStatus,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        is_offline: bool = False,
        error_message: Optional[str] = None,
        response_time_ms: Optional[int] = None
    ) -> ValidationLog:
        """
        Registra um log de validação.

        Args:
            db: Sessão do banco de dados
            activation: Ativação do dispositivo
            status: Status da validação
            ip_address: IP da requisição
            user_agent: User agent
            is_offline: Se estava offline
            error_message: Mensagem de erro (se houve)
            response_time_ms: Tempo de resposta

        Returns:
            ValidationLog criado
        """
        log = ValidationLog(
            device_activation_id=activation.id,
            status=status,
            ip_address=ip_address,
            user_agent=user_agent,
            is_offline=is_offline,
            error_message=error_message,
            validated_at=datetime.utcnow(),
            response_time_ms=str(response_time_ms) if response_time_ms else None
        )

        db.add(log)
        db.commit()
        return log

    @staticmethod
    def get_validation_logs(
        db: Session,
        activation_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[ValidationLog], int]:
        """
        Busca logs de validação de um dispositivo.

        Args:
            db: Sessão do banco de dados
            activation_id: ID da ativação
            skip: Paginação
            limit: Limite

        Returns:
            Tupla (logs, total)
        """
        query = db.query(ValidationLog).filter(
            ValidationLog.device_activation_id == activation_id
        )

        total = query.count()
        logs = query.order_by(
            ValidationLog.validated_at.desc()
        ).offset(skip).limit(limit).all()

        return logs, total
