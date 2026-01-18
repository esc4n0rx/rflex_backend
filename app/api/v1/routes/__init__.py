"""
Exporta todas as rotas da API v1.
"""
from app.api.v1.routes import (
    auth,
    companies,
    plans,
    licenses,
    devices,
    public,
    dashboard
)

__all__ = [
    "auth",
    "companies",
    "plans",
    "licenses",
    "devices",
    "public",
    "dashboard",
]
