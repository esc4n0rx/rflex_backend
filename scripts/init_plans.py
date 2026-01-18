#!/usr/bin/env python3
"""
Script para inicializar os planos padrão do RFlex.

Uso:
    python scripts/init_plans.py
"""
import sys
from pathlib import Path

# Adiciona diretório raiz ao path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.services import PlanService


def main():
    """Inicializa os planos padrão."""
    print("=" * 60)
    print("RFlex License Server - Inicialização de Planos")
    print("=" * 60)
    print()

    db = SessionLocal()

    try:
        print("[*] Criando planos padrão...")
        plans = PlanService.initialize_default_plans(db)

        if plans:
            print(f"[+] {len(plans)} plano(s) criado(s):")
            for plan in plans:
                print(f"   - {plan.name}")
                print(f"     Max coletores: {plan.max_devices if plan.max_devices != -1 else 'Ilimitado'}")
                print(f"     Preço: R$ {plan.price_per_device:.2f}/coletor/mes")
                print()
        else:
            print("[i] Planos padrão já existem. Nenhum plano criado.")

    except Exception as e:
        print(f"[!] Erro: {e}")
        return 1
    finally:
        db.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
