"""
Schemas Pydantic para empresas.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class CompanyBase(BaseModel):
    """Schema base para Company."""
    trading_name: str = Field(..., min_length=2, max_length=255, description="Nome fantasia")
    legal_name: str = Field(..., min_length=2, max_length=255, description="Razão social")
    cnpj: Optional[str] = Field(None, max_length=20, description="CNPJ")
    email: EmailStr = Field(..., description="Email principal")
    phone: Optional[str] = Field(None, max_length=20, description="Telefone")
    address: Optional[str] = Field(None, description="Endereço completo")
    notes: Optional[str] = Field(None, description="Observações")


class CompanyCreate(CompanyBase):
    """Schema para criação de Company."""
    pass


class CompanyUpdate(BaseModel):
    """Schema para atualização de Company."""
    trading_name: Optional[str] = Field(None, min_length=2, max_length=255)
    legal_name: Optional[str] = Field(None, min_length=2, max_length=255)
    cnpj: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class CompanyResponse(CompanyBase):
    """Schema para resposta de Company."""
    id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CompanyListResponse(BaseModel):
    """Schema para lista de empresas com paginação."""
    items: list[CompanyResponse]
    total: int
    page: int
    size: int
    pages: int
