#!/usr/bin/env python3
"""
Script de inicialização completo do banco de dados.

Uso:
    python scripts/init_db.py

Este script:
1. Cria todas as tabelas
2. Cria o administrador master
3. Inicializa os planos padrão
"""
import sys
from pathlib import Path

# Adiciona diretório raiz ao path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.database import engine, Base


def init_database():
    """Inicializa o banco de dados criando todas as tabelas."""
    print("=" * 60)
    print("RFlex License Server - Inicialização do Banco de Dados")
    print("=" * 60)
    print()

    print("[*] Criando tabelas...")
    Base.metadata.create_all(bind=engine)
    print("[+] Tabelas criadas com sucesso!")
    print()

    print("[*] Proximos passos:")
    print("   1. Execute: python scripts/init_admin.py")
    print("   2. Execute: python scripts/init_plans.py")
    print()


if __name__ == "__main__":
    init_database()
