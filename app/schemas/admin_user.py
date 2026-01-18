"""
Schemas Pydantic para usuários administradores.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class AdminUserBase(BaseModel):
    """Schema base para AdminUser."""
    email: EmailStr = Field(..., description="Email de login")
    full_name: str = Field(..., min_length=3, max_length=255, description="Nome completo")


class AdminUserCreate(AdminUserBase):
    """Schema para criação de AdminUser."""
    password: str = Field(..., min_length=8, max_length=100, description="Senha")
    is_superadmin: bool = Field(default=False, description="Se é superadmin")


class AdminUserUpdate(BaseModel):
    """Schema para atualização de AdminUser."""
    full_name: Optional[str] = Field(None, min_length=3, max_length=255)
    password: Optional[str] = Field(None, min_length=8, max_length=100)
    is_active: Optional[bool] = None
    is_superadmin: Optional[bool] = None


class AdminUserResponse(AdminUserBase):
    """Schema para resposta de AdminUser."""
    id: str
    is_active: bool
    is_superadmin: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AdminLogin(BaseModel):
    """Schema para login de administrador."""
    email: EmailStr
    password: str


class Token(BaseModel):
    """Schema para resposta de token JWT."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
