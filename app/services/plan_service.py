"""
Serviço de gerenciamento de planos.
"""
from typing import List, Optional
from sqlalchemy.orm import Session

from app.models import Plan
from app.schemas import PlanCreate, PlanUpdate


class PlanService:
    """Serviço para operações de planos."""

    @staticmethod
    def create_plan(db: Session, plan_data: PlanCreate) -> Plan:
        """
        Cria um novo plano.

        Args:
            db: Sessão do banco de dados
            plan_data: Dados do plano

        Returns:
            Instância de Plan criada

        Raises:
            ValueError: Se nome já existe
        """
        # Verifica nome único
        existing = db.query(Plan).filter(
            Plan.name == plan_data.name
        ).first()
        if existing:
            raise ValueError("Já existe um plano com este nome")

        plan = Plan(**plan_data.model_dump())
        db.add(plan)
        db.commit()
        db.refresh(plan)

        return plan

    @staticmethod
    def get_plan_by_id(db: Session, plan_id: str) -> Optional[Plan]:
        """Busca plano por ID."""
        return db.query(Plan).filter(Plan.id == plan_id).first()

    @staticmethod
    def get_active_plans(db: Session) -> List[Plan]:
        """Retorna todos os planos ativos."""
        return db.query(Plan).filter(
            Plan.is_active == True
        ).order_by(Plan.max_devices).all()

    @staticmethod
    def list_plans(
        db: Session,
        is_active: Optional[bool] = None,
        is_enterprise: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[Plan], int]:
        """
        Lista planos com filtros opcionais.

        Args:
            db: Sessão do banco de dados
            is_active: Filtrar por status ativo
            is_enterprise: Filtrar planos enterprise
            skip: Paginação
            limit: Limite de registros

        Returns:
            Tupla (lista de planos, total)
        """
        query = db.query(Plan)

        if is_active is not None:
            query = query.filter(Plan.is_active == is_active)

        if is_enterprise is not None:
            query = query.filter(Plan.is_enterprise == is_enterprise)

        total = query.count()
        plans = query.order_by(
            Plan.max_devices.asc()
        ).offset(skip).limit(limit).all()

        return plans, total

    @staticmethod
    def update_plan(
        db: Session,
        plan: Plan,
        plan_data: PlanUpdate
    ) -> Plan:
        """Atualiza dados de um plano."""
        update_data = plan_data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(plan, field, value)

        db.commit()
        db.refresh(plan)
        return plan

    @staticmethod
    def delete_plan(db: Session, plan: Plan) -> None:
        """
        Remove um plano.

        ATENÇÃO: Não pode remover plano com licenças vinculadas.
        """
        if plan.licenses:
            raise ValueError("Não é possível remover plano com licenças vinculadas")

        db.delete(plan)
        db.commit()

    @staticmethod
    def initialize_default_plans(db: Session) -> List[Plan]:
        """
        Inicializa os planos padrão do RFlex.

        Args:
            db: Sessão do banco de dados

        Returns:
            Lista de planos criados
        """
        import json

        default_plans = [
            {
                "name": "RFlex Starter",
                "max_devices": 5,
                "price_per_device": 79.0,
                "description": "Plano ideal para pequenas equipes",
                "features": json.dumps([
                    "Até 5 coletores",
                    "Suporte básico",
                    "Atualizações incluídas",
                    "Acesso ao app RFlex Client"
                ]),
                "is_active": True,
                "is_enterprise": False
            },
            {
                "name": "RFlex Pro",
                "max_devices": 20,
                "price_per_device": 49.0,
                "description": "Para equipes em crescimento",
                "features": json.dumps([
                    "Até 20 coletores",
                    "Prioridade em suporte",
                    "Ajustes finos (DPI, RFUI tuning)",
                    "Atualizações incluídas",
                    "Acesso ao app RFlex Client"
                ]),
                "is_active": True,
                "is_enterprise": False
            },
            {
                "name": "RFlex Enterprise",
                "max_devices": -1,  # Ilimitado
                "price_per_device": 0.0,
                "description": "Solução personalizada para grandes operações",
                "features": json.dumps([
                    "Coletores ilimitados",
                    "SLA dedicado",
                    "Customizações exclusivas",
                    "Branding do cliente",
                    "Gerente de conta dedicado",
                    "Treinamento presencial"
                ]),
                "is_active": True,
                "is_enterprise": True
            }
        ]

        created_plans = []
        for plan_data in default_plans:
            # Verifica se já existe
            existing = db.query(Plan).filter(
                Plan.name == plan_data["name"]
            ).first()

            if not existing:
                plan = Plan(**plan_data)
                db.add(plan)
                created_plans.append(plan)

        if created_plans:
            db.commit()

        return created_plans
