"""
Schemas Pydantic para planos de licenciamento.
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator


class PlanBase(BaseModel):
    """Schema base para Plan."""
    name: str = Field(..., min_length=2, max_length=100, description="Nome do plano")
    max_devices: int = Field(..., description="Máximo de coletores (-1 para ilimitado)")
    price_per_device: float = Field(..., ge=0, description="Preço por coletor/mês (R$)")
    description: Optional[str] = Field(None, description="Descrição do plano")
    features: Optional[str] = Field(None, description="Recursos (JSON)")

    @field_validator("max_devices")
    @classmethod
    def validate_max_devices(cls, v: int) -> int:
        if v == -1 or v > 0:
            return v
        raise ValueError("max_devices deve ser -1 (ilimitado) ou maior que 0")


class PlanCreate(PlanBase):
    """Schema para criação de Plan."""
    is_enterprise: bool = Field(default=False, description="Se é plano enterprise")


class PlanUpdate(BaseModel):
    """Schema para atualização de Plan."""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    max_devices: Optional[int] = Field(None)
    price_per_device: Optional[float] = Field(None, ge=0)
    description: Optional[str] = None
    features: Optional[str] = None
    is_active: Optional[bool] = None
    is_enterprise: Optional[bool] = None

    @field_validator("max_devices")
    @classmethod
    def validate_max_devices(cls, v: Optional[int]) -> Optional[int]:
        if v is None or v == -1 or v > 0:
            return v
        raise ValueError("max_devices deve ser -1 (ilimitado) ou maior que 0")


class PlanResponse(PlanBase):
    """Schema para resposta de Plan."""
    id: str
    is_active: bool
    is_enterprise: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PlanListResponse(BaseModel):
    """Schema para lista de planos."""
    items: list[PlanResponse]
    total: int
    page: int
    size: int
    pages: int
