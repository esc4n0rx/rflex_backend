"""
Schemas Pydantic para planos de licenciamento.
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class PlanBase(BaseModel):
    """Schema base para Plan."""
    name: str = Field(..., min_length=2, max_length=100, description="Nome do plano")
    max_devices: int = Field(..., gt=0, description="Máximo de coletores (-1 para ilimitado)")
    price_per_device: float = Field(..., ge=0, description="Preço por coletor/mês (R$)")
    description: Optional[str] = Field(None, description="Descrição do plano")
    features: Optional[str] = Field(None, description="Recursos (JSON)")


class PlanCreate(PlanBase):
    """Schema para criação de Plan."""
    is_enterprise: bool = Field(default=False, description="Se é plano enterprise")


class PlanUpdate(BaseModel):
    """Schema para atualização de Plan."""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    max_devices: Optional[int] = Field(None, gt=0)
    price_per_device: Optional[float] = Field(None, ge=0)
    description: Optional[str] = None
    features: Optional[str] = None
    is_active: Optional[bool] = None
    is_enterprise: Optional[bool] = None


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
