"""
Rotas públicas usadas pelo app RFlex (coletores).
Não requer autenticação de administrador.
"""
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services import LicenseService, DeviceService
from app.schemas import (
    DeviceActivationRequest,
    DeviceActivationResponse,
    DeviceValidationRequest,
    DeviceValidationResponse
)
from app.models import ValidationStatus

router = APIRouter(prefix="/public", tags=["Público (RFlex Client)"])


@router.post("/activate", response_model=DeviceActivationResponse)
def activate_device(
    request: DeviceActivationRequest,
    http_request: Request,
    db: Session = Depends(get_db)
):
    """
    Ativa um coletor (dispositivo) em uma licença.

    Endpoint usado pelo app RFlex Client ao ativar uma licença.
    """
    try:
        activation, token = DeviceService.activate_device(db, request)

        # Busca licença e empresa para resposta
        license = LicenseService.get_license_by_id(db, activation.license_id)

        return DeviceActivationResponse(
            success=True,
            message="Dispositivo ativado com sucesso",
            activation_token=token,
            license_expires_at=license.expires_at,
            company_name=license.company.trading_name,
            plan_name=license.plan.name
        )

    except ValueError as e:
        return DeviceActivationResponse(
            success=False,
            message=str(e),
            activation_token="",
            license_expires_at=datetime.utcnow(),
            company_name="",
            plan_name=""
        )


@router.post("/validate", response_model=DeviceValidationResponse)
def validate_device(
    request: DeviceValidationRequest,
    http_request: Request,
    db: Session = Depends(get_db)
):
    """
    Valida se um dispositivo tem licença válida.

    Endpoint usado pelo app RFlex Client para validar periodicamente.
    """
    start_time = datetime.now()

    # Valida dispositivo
    is_valid, message, license = DeviceService.validate_device(
        db,
        request.device_id,
        request.activation_token,
        request.is_offline
    )

    # Busca ativação para logging
    activation = DeviceService.get_device_by_device_id(db, request.device_id)

    # Registra log
    if activation:
        response_time = int((datetime.now() - start_time).total_seconds() * 1000)
        log_status = ValidationStatus.SUCCESS if is_valid else ValidationStatus.FAILED
        if "tolerância" in message.lower():
            log_status = ValidationStatus.GRACE_PERIOD

        DeviceService.log_validation(
            db,
            activation,
            status=log_status,
            ip_address=http_request.client.host if http_request.client else None,
            user_agent=http_request.headers.get("user-agent"),
            is_offline=request.is_offline,
            error_message=None if is_valid else message,
            response_time_ms=response_time
        )

    # Monta resposta
    response = DeviceValidationResponse(
        valid=is_valid,
        message=message
    )

    if is_valid and license:
        response.license_expires_at = license.expires_at
        response.company_name = license.company.trading_name
        response.plan_name = license.plan.name

        # Calcula fim do período de tolerância
        if activation.last_validated_at:
            from app.core.config import settings
            from datetime import timedelta
            response.grace_period_until = activation.last_validated_at + timedelta(
                hours=settings.grace_period_hours
            )

    return response


@router.get("/license/{license_code}/info")
def get_license_info(
    license_code: str,
    db: Session = Depends(get_db)
):
    """
    Retorna informações públicas sobre uma licença (usado para pré-validação).

    Não expõe informações sensíveis.
    """
    from app.models import License

    license = db.query(License).filter(
        License.code == license_code.upper()
    ).first()

    if not license:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Licença não encontrada"
        )

    return {
        "code": license.code,
        "status": license.status.value,
        "expires_at": license.expires_at,
        "is_valid": license.is_valid(),
        "plan_name": license.plan.name,
        "company_name": license.company.trading_name,
        "max_devices": license.plan.max_devices,
        "active_devices": license.get_active_devices_count(),
        "available_slots": LicenseService.get_available_slots(license)
    }
