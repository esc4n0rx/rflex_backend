"""
Schemas Pydantic para ativação e validação de dispositivos.
"""
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, IPvAnyAddress


class DeviceActivationRequest(BaseModel):
    """
    Schema para requisição de ativação de dispositivo.

    Enviado pelo app RFlex ao ativar uma licença.
    """
    license_code: str = Field(..., min_length=32, max_length=32, description="Código da licença")
    device_id: str = Field(..., min_length=1, description="UUID do dispositivo")
    device_name: Optional[str] = Field(None, description="Nome do coletor")
    device_manufacturer: Optional[str] = Field(None, description="Fabricante")
    device_model: Optional[str] = Field(None, description="Modelo")
    android_version: Optional[str] = Field(None, description="Versão do Android")
    app_version: Optional[str] = Field(None, description="Versão do app RFlex")
    hardware_info: Optional[Dict[str, Any]] = Field(None, description="Infos adicionais")


class DeviceActivationResponse(BaseModel):
    """
    Schema para resposta de ativação bem-sucedida.

    O app deve salvar este token para validações futuras.
    """
    success: bool
    message: str
    activation_token: str = Field(..., description="Token de ativação")
    license_expires_at: datetime = Field(..., description="Data de expiração")
    company_name: str = Field(..., description="Nome da empresa")
    plan_name: str = Field(..., description="Nome do plano")


class DeviceValidationRequest(BaseModel):
    """
    Schema para requisição de validação de dispositivo.

    Enviado periodicamente pelo app RFlex.
    """
    activation_token: str = Field(..., description="Token de ativação")
    device_id: str = Field(..., description="UUID do dispositivo")
    is_offline: bool = Field(default=False, description="Se está em modo offline")


class DeviceValidationResponse(BaseModel):
    """
    Schema para resposta de validação de dispositivo.

    O app usa essa resposta para permitir ou bloquear o acesso.
    """
    valid: bool
    message: str
    license_expires_at: Optional[datetime] = None
    grace_period_until: Optional[datetime] = Field(
        None,
        description="Fim do período de tolerância offline"
    )
    company_name: Optional[str] = None
    plan_name: Optional[str] = None


class DeviceRevocationRequest(BaseModel):
    """Schema para revogação de dispositivo (admin)."""
    reason: Optional[str] = Field(None, description="Motivo da revogação")


class DeviceReactivationRequest(BaseModel):
    """Schema para reativação de dispositivo (admin)."""
    pass


class DeviceActivationDetail(BaseModel):
    """Schema para detalhes de ativação de dispositivo."""
    id: str
    device_id: str
    device_name: Optional[str]
    device_manufacturer: Optional[str]
    device_model: Optional[str]
    android_version: Optional[str]
    app_version: Optional[str]
    activated_at: datetime
    last_validated_at: Optional[datetime]
    is_active: bool
    is_revoked: bool
    revoked_at: Optional[datetime]
    revoke_reason: Optional[str]

    class Config:
        from_attributes = True


class DeviceListResponse(BaseModel):
    """Schema para lista de dispositivos."""
    items: list[DeviceActivationDetail]
    total: int
    page: int
    size: int
    pages: int
