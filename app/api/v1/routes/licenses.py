"""
Rotas de gerenciamento de licenças.
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import Response, FileResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_admin
from app.models import AdminUser, LicenseStatus
from app.services import LicenseService, DeviceService
from app.schemas import (
    LicenseCreate,
    LicenseUpdate,
    LicenseRenew,
    LicenseResponse,
    LicenseListResponse,
    LicenseWithDevices
)
from app.utils import generate_license_qrcode, generate_license_pdf

router = APIRouter(prefix="/licenses", tags=["Licenças"])


@router.post("", response_model=LicenseResponse, status_code=status.HTTP_201_CREATED)
def create_license(
    license_data: LicenseCreate,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """Cria uma nova licença."""
    try:
        license = LicenseService.create_license(
            db,
            license_data,
            validity_days=license_data.validity_days
        )
        return license
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("", response_model=LicenseListResponse)
def list_licenses(
    company_id: Optional[str] = None,
    status: Optional[LicenseStatus] = None,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """Lista licenças com paginação e filtros."""
    skip = (page - 1) * size
    licenses, total = LicenseService.list_licenses(
        db,
        company_id=company_id,
        status=status,
        skip=skip,
        limit=size
    )

    pages = (total + size - 1) // size

    return LicenseListResponse(
        items=licenses,
        total=total,
        page=page,
        size=size,
        pages=pages
    )


@router.get("/{license_id}", response_model=LicenseWithDevices)
def get_license(
    license_id: str,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """Retorna detalhes de uma licença com seus dispositivos."""
    license = LicenseService.get_license_by_id(db, license_id)
    if not license:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Licença não encontrada"
        )

    # Busca dispositivos
    devices, _ = DeviceService.list_devices(
        db,
        license_id=license_id,
        limit=1000
    )

    return LicenseWithDevices(
        **LicenseResponse.model_validate(license).model_dump(),
        devices=[d.__dict__ for d in devices]
    )


@router.patch("/{license_id}", response_model=LicenseResponse)
def update_license(
    license_id: str,
    license_data: LicenseUpdate,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """Atualiza dados de uma licença."""
    license = LicenseService.get_license_by_id(db, license_id)
    if not license:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Licença não encontrada"
        )

    updated = LicenseService.update_license(db, license, license_data)
    return updated


@router.post("/{license_id}/renew", response_model=LicenseResponse)
def renew_license(
    license_id: str,
    renewal_data: LicenseRenew,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """Renova a validade de uma licença."""
    license = LicenseService.get_license_by_id(db, license_id)
    if not license:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Licença não encontrada"
        )

    renewed = LicenseService.renew_license(db, license, renewal_data.days)
    return renewed


@router.post("/{license_id}/suspend", response_model=LicenseResponse)
def suspend_license(
    license_id: str,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """Suspende uma licença."""
    license = LicenseService.get_license_by_id(db, license_id)
    if not license:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Licença não encontrada"
        )

    suspended = LicenseService.suspend_license(db, license)
    return suspended


@router.post("/{license_id}/activate", response_model=LicenseResponse)
def activate_license(
    license_id: str,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """Ativa uma licença inativa/suspensa."""
    license = LicenseService.get_license_by_id(db, license_id)
    if not license:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Licença não encontrada"
        )

    try:
        activated = LicenseService.activate_license(db, license)
        return activated
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{license_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_license(
    license_id: str,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """Remove uma licença."""
    license = LicenseService.get_license_by_id(db, license_id)
    if not license:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Licença não encontrada"
        )

    LicenseService.delete_license(db, license)


@router.get("/{license_id}/devices")
def list_license_devices(
    license_id: str,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """Lista todos os dispositivos de uma licença."""
    license = LicenseService.get_license_by_id(db, license_id)
    if not license:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Licença não encontrada"
        )

    devices, total = DeviceService.list_devices(
        db,
        license_id=license_id,
        is_active=is_active,
        limit=1000
    )

    return {
        "license_id": license_id,
        "total": total,
        "items": devices
    }


@router.get("/{license_id}/qrcode")
def get_license_qrcode(
    license_id: str,
    size: int = Query(300, ge=100, le=1000),
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """
    Gera e retorna o QR Code de uma licença.

    Retorna uma imagem PNG com o QR Code para ativação da licença.
    """
    license = LicenseService.get_license_by_id(db, license_id)
    if not license:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Licença não encontrada"
        )

    # Gera QR Code
    qrcode_bytes = generate_license_qrcode(license, size=size)

    return Response(
        content=qrcode_bytes,
        media_type="image/png",
        headers={
            "Content-Disposition": f"inline; filename=qrcode_{license.code}.png"
        }
    )


@router.get("/{license_id}/pdf")
def get_license_pdf(
    license_id: str,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """
    Gera e retorna um PDF com os detalhes da licença.

    O PDF contém:
    - QR Code para ativação
    - Código da licença formatado
    - Informações da empresa e plano
    - Instruções de ativação
    """
    license = LicenseService.get_license_by_id(db, license_id)
    if not license:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Licença não encontrada"
        )

    # Gera PDF
    pdf_bytes = generate_license_pdf(license)

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=license_{license.code}.pdf"
        }
    )
