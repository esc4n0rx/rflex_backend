"""
Schemas Pydantic para licenças.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from app.models.license import LicenseStatus


class LicenseBase(BaseModel):
    """Schema base para License."""
    company_id: str = Field(..., description="ID da empresa")
    plan_id: str = Field(..., description="ID do plano")
    notes: Optional[str] = Field(None, description="Observações")


class LicenseCreate(LicenseBase):
    """Schema para criação de License."""
    validity_days: int = Field(
        default=30,
        ge=1,
        le=365,
        description="Validade em dias"
    )


class LicenseUpdate(BaseModel):
    """Schema para atualização de License."""
    status: Optional[LicenseStatus] = None
    notes: Optional[str] = None


class LicenseRenew(BaseModel):
    """Schema para renovação de License."""
    days: int = Field(..., ge=1, le=365, description="Dias a adicionar à validade")


class LicenseResponse(LicenseBase):
    """Schema para resposta de License."""
    id: str
    code: str
    status: LicenseStatus
    expires_at: datetime
    created_at: datetime
    updated_at: datetime
    is_valid: bool = Field(..., description="Se a licença está válida")
    is_expired: bool = Field(..., description="Se a licença está expirada")
    active_devices: int = Field(..., description="Número de dispositivos ativos")
    max_devices: int = Field(..., description="Máximo de dispositivos permitidos")

    class Config:
        from_attributes = True


class LicenseListResponse(BaseModel):
    """Schema para lista de licenças."""
    items: list[LicenseResponse]
    total: int
    page: int
    size: int
    pages: int


class LicenseWithDevices(LicenseResponse):
    """Schema para licença com dispositivos."""
    devices: list[dict] = Field(default_factory=list, description="Dispositivos ativados")
