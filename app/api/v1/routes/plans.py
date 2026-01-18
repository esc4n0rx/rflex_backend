"""
Rotas de gerenciamento de planos.
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_admin
from app.models import AdminUser
from app.services import PlanService
from app.schemas import (
    PlanCreate,
    PlanUpdate,
    PlanResponse,
    PlanListResponse
)

router = APIRouter(prefix="/plans", tags=["Planos"])


@router.post("", response_model=PlanResponse, status_code=status.HTTP_201_CREATED)
def create_plan(
    plan_data: PlanCreate,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """Cria um novo plano de licenciamento."""
    try:
        plan = PlanService.create_plan(db, plan_data)
        return plan
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("", response_model=PlanListResponse)
def list_plans(
    is_active: Optional[bool] = None,
    is_enterprise: Optional[bool] = None,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """Lista planos com paginação e filtros."""
    skip = (page - 1) * size
    plans, total = PlanService.list_plans(
        db,
        is_active=is_active,
        is_enterprise=is_enterprise,
        skip=skip,
        limit=size
    )

    pages = (total + size - 1) // size

    return PlanListResponse(
        items=plans,
        total=total,
        page=page,
        size=size,
        pages=pages
    )


@router.get("/active", response_model=list[PlanResponse])
def get_active_plans(
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """Retorna todos os planos ativos disponíveis."""
    plans = PlanService.get_active_plans(db)
    return plans


@router.get("/{plan_id}", response_model=PlanResponse)
def get_plan(
    plan_id: str,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """Retorna detalhes de um plano específico."""
    plan = PlanService.get_plan_by_id(db, plan_id)
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plano não encontrado"
        )
    return plan


@router.patch("/{plan_id}", response_model=PlanResponse)
def update_plan(
    plan_id: str,
    plan_data: PlanUpdate,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """Atualiza dados de um plano."""
    plan = PlanService.get_plan_by_id(db, plan_id)
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plano não encontrado"
        )

    updated = PlanService.update_plan(db, plan, plan_data)
    return updated


@router.delete("/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_plan(
    plan_id: str,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """Remove um plano."""
    plan = PlanService.get_plan_by_id(db, plan_id)
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plano não encontrado"
        )

    try:
        PlanService.delete_plan(db, plan)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
