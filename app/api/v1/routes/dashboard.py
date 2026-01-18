"""
Rotas do dashboard administrativo.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from app.core.database import get_db
from app.core.security import get_current_admin
from app.models import AdminUser, Company, License, LicenseStatus, DeviceActivation, Plan
from app.schemas import DashboardStats, PlanUsageStats
from app.services import LicenseService

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/stats", response_model=DashboardStats)
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """Retorna estatísticas gerais do dashboard."""
    # Empresas
    total_companies = db.query(Company).count()
    active_companies = db.query(Company).filter(Company.is_active == True).count()

    # Licenças
    total_licenses = db.query(License).count()
    active_licenses = db.query(License).filter(License.status == LicenseStatus.ACTIVE).count()
    expired_licenses = db.query(License).filter(License.status == LicenseStatus.EXPIRED).count()
    inactive_licenses = db.query(License).filter(License.status == LicenseStatus.INACTIVE).count()

    # Dispositivos
    total_devices = db.query(DeviceActivation).count()
    active_devices = db.query(DeviceActivation).filter(DeviceActivation.is_active == True).count()
    revoked_devices = db.query(DeviceActivation).filter(DeviceActivation.is_revoked == True).count()

    return DashboardStats(
        total_companies=total_companies,
        active_companies=active_companies,
        total_licenses=total_licenses,
        active_licenses=active_licenses,
        expired_licenses=expired_licenses,
        inactive_licenses=inactive_licenses,
        total_devices=total_devices,
        active_devices=active_devices,
        revoked_devices=revoked_devices
    )


@router.get("/plans-usage", response_model=list[PlanUsageStats])
def get_plans_usage(
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """Retorna estatísticas de uso por plano."""
    plans = db.query(Plan).filter(Plan.is_active == True).all()

    stats = []
    for plan in plans:
        # Licenças deste plano
        total_licenses = db.query(License).filter(License.plan_id == plan.id).count()
        active_licenses = db.query(License).filter(
            License.plan_id == plan.id,
            License.status == LicenseStatus.ACTIVE
        ).count()

        # Dispositivos ativos neste plano
        total_devices = db.query(DeviceActivation).join(License).filter(
            License.plan_id == plan.id
        ).count()

        active_devices = db.query(DeviceActivation).join(License).filter(
            License.plan_id == plan.id,
            DeviceActivation.is_active == True
        ).count()

        # Taxa de ocupação
        if plan.max_devices == -1:
            occupancy_rate = 0.0  # Enterprise não tem taxa
        elif active_licenses > 0:
            # Ocupação = dispositivos ativos / (licenças ativas * max por plano)
            max_possible = active_licenses * plan.max_devices
            occupancy_rate = (active_devices / max_possible * 100) if max_possible > 0 else 0
        else:
            occupancy_rate = 0.0

        stats.append(PlanUsageStats(
            plan_name=plan.name,
            plan_id=plan.id,
            total_licenses=total_licenses,
            active_licenses=active_licenses,
            total_devices=total_devices,
            active_devices=active_devices,
            occupancy_rate=round(occupancy_rate, 2)
        ))

    return stats


@router.get("/recent-activations")
def get_recent_activations(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """Retorna as ativações mais recentes."""
    activations = db.query(DeviceActivation).order_by(
        DeviceActivation.created_at.desc()
    ).limit(limit).all()

    return [
        {
            "id": a.id,
            "device_name": a.device_name,
            "device_model": a.device_model,
            "company_name": a.license.company.trading_name,
            "plan_name": a.license.plan.name,
            "activated_at": a.activated_at,
            "is_active": a.is_active
        }
        for a in activations
    ]


@router.get("/expiring-licenses")
def get_expiring_licenses(
    days: int = 7,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """Retorna licenças que expiram em breve."""
    licenses = LicenseService.get_expiring_licenses(db, days)

    return [
        {
            "id": l.id,
            "code": l.code,
            "company_name": l.company.trading_name,
            "plan_name": l.plan.name,
            "expires_at": l.expires_at,
            "active_devices": l.get_active_devices_count(),
            "max_devices": l.plan.max_devices
        }
        for l in licenses
    ]
