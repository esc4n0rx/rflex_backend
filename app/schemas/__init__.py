"""
Exporta todos os schemas Pydantic.
"""
from app.schemas.admin_user import (
    AdminUserBase,
    AdminUserCreate,
    AdminUserUpdate,
    AdminUserResponse,
    AdminLogin,
    Token,
)
from app.schemas.company import (
    CompanyBase,
    CompanyCreate,
    CompanyUpdate,
    CompanyResponse,
    CompanyListResponse,
)
from app.schemas.plan import (
    PlanBase,
    PlanCreate,
    PlanUpdate,
    PlanResponse,
    PlanListResponse,
)
from app.schemas.license import (
    LicenseBase,
    LicenseCreate,
    LicenseUpdate,
    LicenseRenew,
    LicenseResponse,
    LicenseListResponse,
    LicenseWithDevices,
)
from app.schemas.device import (
    DeviceActivationRequest,
    DeviceActivationResponse,
    DeviceValidationRequest,
    DeviceValidationResponse,
    DeviceRevocationRequest,
    DeviceReactivationRequest,
    DeviceActivationDetail,
    DeviceListResponse,
)
from app.schemas.dashboard import (
    DashboardStats,
    LicenseStatusBreakdown,
    DeviceStatusBreakdown,
    PlanUsageStats,
)

__all__ = [
    # Admin
    "AdminUserBase",
    "AdminUserCreate",
    "AdminUserUpdate",
    "AdminUserResponse",
    "AdminLogin",
    "Token",
    # Company
    "CompanyBase",
    "CompanyCreate",
    "CompanyUpdate",
    "CompanyResponse",
    "CompanyListResponse",
    # Plan
    "PlanBase",
    "PlanCreate",
    "PlanUpdate",
    "PlanResponse",
    "PlanListResponse",
    # License
    "LicenseBase",
    "LicenseCreate",
    "LicenseUpdate",
    "LicenseRenew",
    "LicenseResponse",
    "LicenseListResponse",
    "LicenseWithDevices",
    # Device
    "DeviceActivationRequest",
    "DeviceActivationResponse",
    "DeviceValidationRequest",
    "DeviceValidationResponse",
    "DeviceRevocationRequest",
    "DeviceReactivationRequest",
    "DeviceActivationDetail",
    "DeviceListResponse",
    # Dashboard
    "DashboardStats",
    "LicenseStatusBreakdown",
    "DeviceStatusBreakdown",
    "PlanUsageStats",
]
