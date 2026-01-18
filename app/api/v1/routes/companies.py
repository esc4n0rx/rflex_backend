"""
Rotas de gerenciamento de empresas.
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_admin, get_current_superadmin
from app.models import AdminUser
from app.services import CompanyService
from app.schemas import (
    CompanyCreate,
    CompanyUpdate,
    CompanyResponse,
    CompanyListResponse
)

router = APIRouter(prefix="/companies", tags=["Empresas"])


@router.post("", response_model=CompanyResponse, status_code=status.HTTP_201_CREATED)
def create_company(
    company_data: CompanyCreate,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """
    Cria uma nova empresa.

    Requer autenticação de administrador.
    """
    try:
        company = CompanyService.create_company(db, company_data)
        return company
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("", response_model=CompanyListResponse)
def list_companies(
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """
    Lista empresas com paginação e filtros.

    - is_active: Filtra por status ativo/inativo
    - search: Busca por nome, CNPJ ou email
    - page: Número da página (inicia em 1)
    - size: Itens por página
    """
    skip = (page - 1) * size
    companies, total = CompanyService.list_companies(
        db,
        is_active=is_active,
        search=search,
        skip=skip,
        limit=size
    )

    pages = (total + size - 1) // size

    return CompanyListResponse(
        items=companies,
        total=total,
        page=page,
        size=size,
        pages=pages
    )


@router.get("/{company_id}", response_model=CompanyResponse)
def get_company(
    company_id: str,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """
    Retorna detalhes de uma empresa específica.
    """
    company = CompanyService.get_company_by_id(db, company_id)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Empresa não encontrada"
        )
    return company


@router.patch("/{company_id}", response_model=CompanyResponse)
def update_company(
    company_id: str,
    company_data: CompanyUpdate,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """
    Atualiza dados de uma empresa.
    """
    company = CompanyService.get_company_by_id(db, company_id)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Empresa não encontrada"
        )

    updated = CompanyService.update_company(db, company, company_data)
    return updated


@router.delete("/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_company(
    company_id: str,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_superadmin)
):
    """
    Remove uma empresa.

    ATENÇÃO: Isso também removerá todas as licenças e ativações vinculadas.
    Requer superadmin.
    """
    company = CompanyService.get_company_by_id(db, company_id)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Empresa não encontrada"
        )

    CompanyService.delete_company(db, company)


@router.get("/{company_id}/stats")
def get_company_statistics(
    company_id: str,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """
    Retorna estatísticas de uma empresa.
    """
    company = CompanyService.get_company_by_id(db, company_id)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Empresa não encontrada"
        )

    stats = CompanyService.get_company_stats(db, company)
    return {
        "company_id": company_id,
        "company_name": company.trading_name,
        **stats
    }
