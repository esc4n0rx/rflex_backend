"""
Rotas de gerenciamento de dispositivos (coletores).
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_admin
from app.models import AdminUser
from app.services import DeviceService
from app.schemas import (
    DeviceRevocationRequest,
    DeviceActivationDetail,
    DeviceListResponse
)

router = APIRouter(prefix="/devices", tags=["Dispositivos"])


@router.get("", response_model=DeviceListResponse)
def list_devices(
    license_id: Optional[str] = None,
    is_active: Optional[bool] = None,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """Lista dispositivos com paginação e filtros."""
    skip = (page - 1) * size
    devices, total = DeviceService.list_devices(
        db,
        license_id=license_id,
        is_active=is_active,
        skip=skip,
        limit=size
    )

    pages = (total + size - 1) // size

    return DeviceListResponse(
        items=devices,
        total=total,
        page=page,
        size=size,
        pages=pages
    )


@router.get("/{activation_id}", response_model=DeviceActivationDetail)
def get_device(
    activation_id: str,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """Retorna detalhes de um dispositivo específico."""
    device = DeviceService.get_device_activation(db, activation_id)
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dispositivo não encontrado"
        )
    return device


@router.post("/{activation_id}/revoke", response_model=DeviceActivationDetail)
def revoke_device(
    activation_id: str,
    request: DeviceRevocationRequest,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """Revoga um dispositivo (libera vaga na licença)."""
    device = DeviceService.get_device_activation(db, activation_id)
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dispositivo não encontrado"
        )

    revoked = DeviceService.revoke_device(db, device, request.reason)
    return revoked


@router.post("/{activation_id}/reactivate", response_model=DeviceActivationDetail)
def reactivate_device(
    activation_id: str,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """Reativa um dispositivo revogado."""
    device = DeviceService.get_device_activation(db, activation_id)
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dispositivo não encontrado"
        )

    try:
        reactivated = DeviceService.reactivate_device(db, device)
        return reactivated
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{activation_id}/logs")
def get_device_logs(
    activation_id: str,
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """Retorna logs de validação de um dispositivo."""
    device = DeviceService.get_device_activation(db, activation_id)
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dispositivo não encontrado"
        )

    skip = (page - 1) * size
    logs, total = DeviceService.get_validation_logs(
        db,
        activation_id,
        skip=skip,
        limit=size
    )

    return {
        "activation_id": activation_id,
        "total": total,
        "page": page,
        "size": size,
        "items": logs
    }
