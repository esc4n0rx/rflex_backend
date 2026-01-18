"""
Schemas Pydantic para dashboard e métricas.
"""
from pydantic import BaseModel, Field
from typing import Optional


class DashboardStats(BaseModel):
    """Schema para estatísticas do dashboard."""
    total_companies: int = Field(..., description="Total de empresas cadastradas")
    active_companies: int = Field(..., description="Empresas ativas")
    total_licenses: int = Field(..., description="Total de licenças")
    active_licenses: int = Field(..., description="Licenças ativas")
    expired_licenses: int = Field(..., description="Licenças expiradas")
    inactive_licenses: int = Field(..., description="Licenças inativas (não ativadas)")
    total_devices: int = Field(..., description="Total de dispositivos ativados")
    active_devices: int = Field(..., description="Dispositivos ativos")
    revoked_devices: int = Field(..., description="Dispositivos revogados")


class LicenseStatusBreakdown(BaseModel):
    """Schema para breakdown de status de licenças."""
    active: int
    inactive: int
    expired: int
    suspended: int


class DeviceStatusBreakdown(BaseModel):
    """Schema para breakdown de status de dispositivos."""
    active: int
    revoked: int


class PlanUsageStats(BaseModel):
    """Schema para estatísticas de uso por plano."""
    plan_name: str
    plan_id: str
    total_licenses: int
    active_licenses: int
    total_devices: int
    active_devices: int
    occupancy_rate: float = Field(..., description="Taxa de ocupação (0-100)")
