"""
Serviço de gerenciamento de empresas.
"""
from typing import List, Optional
from sqlalchemy.orm import Session

from app.models import Company
from app.schemas import CompanyCreate, CompanyUpdate


class CompanyService:
    """Serviço para operações de empresas."""

    @staticmethod
    def create_company(db: Session, company_data: CompanyCreate) -> Company:
        """
        Cria uma nova empresa.

        Args:
            db: Sessão do banco de dados
            company_data: Dados da empresa

        Returns:
            Instância de Company criada

        Raises:
            ValueError: Se CNPJ já cadastrado
        """
        # Verifica CNPJ único
        if company_data.cnpj:
            existing = db.query(Company).filter(
                Company.cnpj == company_data.cnpj
            ).first()
            if existing:
                raise ValueError("CNPJ já cadastrado")

        company = Company(**company_data.model_dump())
        db.add(company)
        db.commit()
        db.refresh(company)

        return company

    @staticmethod
    def get_company_by_id(db: Session, company_id: str) -> Optional[Company]:
        """Busca empresa por ID."""
        return db.query(Company).filter(Company.id == company_id).first()

    @staticmethod
    def get_company_by_cnpj(db: Session, cnpj: str) -> Optional[Company]:
        """Busca empresa por CNPJ."""
        return db.query(Company).filter(Company.cnpj == cnpj).first()

    @staticmethod
    def list_companies(
        db: Session,
        is_active: Optional[bool] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[Company], int]:
        """
        Lista empresas com filtros opcionais.

        Args:
            db: Sessão do banco de dados
            is_active: Filtrar por status ativo
            search: Buscar por nome/CNPJ/email
            skip: Paginação
            limit: Limite de registros

        Returns:
            Tupla (lista de empresas, total)
        """
        query = db.query(Company)

        if is_active is not None:
            query = query.filter(Company.is_active == is_active)

        if search:
            search_term = f"%{search}%"
            query = query.filter(
                (Company.trading_name.ilike(search_term)) |
                (Company.legal_name.ilike(search_term)) |
                (Company.cnpj.ilike(search_term)) |
                (Company.email.ilike(search_term))
            )

        total = query.count()
        companies = query.order_by(
            Company.created_at.desc()
        ).offset(skip).limit(limit).all()

        return companies, total

    @staticmethod
    def update_company(
        db: Session,
        company: Company,
        company_data: CompanyUpdate
    ) -> Company:
        """Atualiza dados de uma empresa."""
        update_data = company_data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(company, field, value)

        db.commit()
        db.refresh(company)
        return company

    @staticmethod
    def delete_company(db: Session, company: Company) -> None:
        """
        Remove uma empresa.

        ATENÇÃO: Isso cascade deletará todas as licenças e ativações.
        """
        db.delete(company)
        db.commit()

    @staticmethod
    def get_company_stats(db: Session, company: Company) -> dict:
        """
        Retorna estatísticas de uma empresa.

        Args:
            db: Sessão do banco de dados
            company: Instância de Company

        Returns:
            Dicionário com estatísticas
        """
        from app.models import License, LicenseStatus, DeviceActivation

        # Total de licenças
        total_licenses = db.query(License).filter(
            License.company_id == company.id
        ).count()

        # Licenças ativas
        active_licenses = db.query(License).filter(
            License.company_id == company.id,
            License.status == LicenseStatus.ACTIVE
        ).count()

        # Licenças expiradas
        expired_licenses = db.query(License).filter(
            License.company_id == company.id,
            License.status == LicenseStatus.EXPIRED
        ).count()

        # Total de dispositivos ativos
        active_devices = db.query(DeviceActivation).join(License).filter(
            License.company_id == company.id,
            DeviceActivation.is_active == True
        ).count()

        return {
            "total_licenses": total_licenses,
            "active_licenses": active_licenses,
            "expired_licenses": expired_licenses,
            "active_devices": active_devices,
        }
