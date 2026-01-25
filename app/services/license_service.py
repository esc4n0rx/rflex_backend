"""
Serviço de gerenciamento de licenças.
"""
from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.models import License, LicenseStatus, DeviceActivation, Company, Plan
from app.schemas import LicenseCreate, LicenseUpdate
from app.utils.license_code import generate_license_code


class LicenseService:
    """Serviço para operações de licença."""

    @staticmethod
    def create_license(
        db: Session,
        license_data: LicenseCreate,
        validity_days: int
    ) -> License:
        """
        Cria uma nova licença.

        Args:
            db: Sessão do banco de dados
            license_data: Dados da licença
            validity_days: Dias de validade

        Returns:
            Instância de License criada

        Raises:
            ValueError: Se empresa ou plano não existirem
        """
        # Verifica se a empresa existe
        company = db.query(Company).filter(Company.id == license_data.company_id).first()
        if not company:
            raise ValueError("Empresa não encontrada")

        # Verifica se o plano existe
        plan = db.query(Plan).filter(Plan.id == license_data.plan_id).first()
        if not plan:
            raise ValueError("Plano não encontrado")

        # Gera código único
        code = generate_license_code()

        # Calcula data de expiração
        expires_at = datetime.utcnow() + timedelta(days=validity_days)

        # Cria licença
        license = License(
            code=code,
            company_id=license_data.company_id,
            plan_id=license_data.plan_id,
            notes=license_data.notes,
            status=LicenseStatus.INACTIVE,
            expires_at=expires_at
        )

        db.add(license)
        db.commit()
        db.refresh(license)

        return license

    @staticmethod
    def get_license_by_id(db: Session, license_id: str) -> Optional[License]:
        """Busca licença por ID."""
        return db.query(License).filter(License.id == license_id).first()

    @staticmethod
    def get_license_by_code(db: Session, code: str) -> Optional[License]:
        """Busca licença por código."""
        return db.query(License).filter(License.code == code).first()

    @staticmethod
    def list_licenses(
        db: Session,
        company_id: Optional[str] = None,
        status: Optional[LicenseStatus] = None,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[License], int]:
        """
        Lista licenças com filtros opcionais.

        Args:
            db: Sessão do banco de dados
            company_id: Filtrar por empresa (opcional)
            status: Filtrar por status (opcional)
            skip: Quantos registros pular (paginação)
            limit: Limite de registros

        Returns:
            Tupla (lista de licenças, total de registros)
        """
        query = db.query(License)

        # Aplica filtros
        if company_id:
            query = query.filter(License.company_id == company_id)
        if status:
            query = query.filter(License.status == status)

        # Conta total
        total = query.count()

        # Aplica paginação
        licenses = query.order_by(License.created_at.desc()).offset(skip).limit(limit).all()

        return licenses, total

    @staticmethod
    def update_license(
        db: Session,
        license: License,
        license_data: LicenseUpdate
    ) -> License:
        """Atualiza dados de uma licença."""
        if license_data.status is not None:
            license.status = license_data.status
        if license_data.notes is not None:
            license.notes = license_data.notes

        db.commit()
        db.refresh(license)
        return license

    @staticmethod
    def renew_license(db: Session, license: License, days: int) -> License:
        """
        Renova a validade de uma licença.

        Args:
            db: Sessão do banco de dados
            license: Licença a renovar
            days: Dias a adicionar

        Returns:
            Licença atualizada
        """
        # Se já expirou, conta a partir de agora
        if license.is_expired:
            license.expires_at = datetime.utcnow() + timedelta(days=days)
        else:
            # Se não expirou, adiciona à data atual
            license.expires_at = license.expires_at + timedelta(days=days)

        # Se estava expirada/suspensa, reativa
        if license.status in [LicenseStatus.EXPIRED, LicenseStatus.SUSPENDED]:
            license.status = LicenseStatus.ACTIVE

        db.commit()
        db.refresh(license)
        return license

    @staticmethod
    def suspend_license(db: Session, license: License) -> License:
        """Suspende uma licença."""
        license.status = LicenseStatus.SUSPENDED
        db.commit()
        db.refresh(license)
        return license

    @staticmethod
    def activate_license(db: Session, license: License) -> License:
        """Ativa uma licença."""
        if license.is_expired:
            raise ValueError("Não é possível ativar licença expirada. Renove primeiro.")

        license.status = LicenseStatus.ACTIVE
        db.commit()
        db.refresh(license)
        return license

    @staticmethod
    def delete_license(db: Session, license: License) -> None:
        """Remove uma licença."""
        db.delete(license)
        db.commit()

    @staticmethod
    def check_availability(license: License) -> bool:
        """
        Verifica se há vagas disponíveis na licença.

        Args:
            license: Instância de License

        Returns:
            True se há vagas disponíveis
        """
        plan = license.plan

        # Plano enterprise (ilimitado)
        if plan.max_devices == -1:
            return True

        # Conta dispositivos ativos
        active_count = license.get_active_devices_count()

        return active_count < plan.max_devices

    @staticmethod
    def get_available_slots(license: License) -> int:
        """
        Retorna o número de vagas disponíveis.

        Args:
            license: Instância de License

        Returns:
            Número de vagas disponíveis (-1 para ilimitado)
        """
        plan = license.plan

        # Plano enterprise
        if plan.max_devices == -1:
            return -1

        active_count = license.get_active_devices_count()
        return max(0, plan.max_devices - active_count)

    @staticmethod
    def get_expiring_licenses(
        db: Session,
        days: int = 7
    ) -> List[License]:
        """
        Retorna licenças que expiram em breve.

        Args:
            db: Sessão do banco de dados
            days: Dias até expiração

        Returns:
            Lista de licenças expirando em breve
        """
        cutoff_date = datetime.utcnow() + timedelta(days=days)

        return db.query(License).filter(
            and_(
                License.status == LicenseStatus.ACTIVE,
                License.expires_at <= cutoff_date,
                License.expires_at > datetime.utcnow()
            )
        ).all()

    @staticmethod
    def mark_expired_licenses(db: Session) -> int:
        """
        Marca licenças expiradas como EXPIRED.

        Args:
            db: Sessão do banco de dados

        Returns:
            Número de licenças atualizadas
        """
        now = datetime.utcnow()

        # Busca licenças ativas que expiraram
        expired_licenses = db.query(License).filter(
            and_(
                License.status == LicenseStatus.ACTIVE,
                License.expires_at < now
            )
        ).all()

        # Atualiza status
        count = 0
        for license in expired_licenses:
            license.status = LicenseStatus.EXPIRED
            count += 1

        db.commit()
        return count
