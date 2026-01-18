#!/usr/bin/env python3
"""
Script para criar uma nova migration Alembic.

Uso:
    python scripts/create_migration.py "nome_da_migration"
"""
import sys
from pathlib import Path

# Adiciona diretório raiz ao path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def main():
    """Cria uma nova migration."""
    if len(sys.argv) < 2:
        print("Uso: python scripts/create_migration.py <nome_da_migration>")
        print("Exemplo: python scripts/create_migration.py add_user_preferences")
        return 1

    migration_name = sys.argv[1]
    print(f"Criando migration: {migration_name}")

    import subprocess

    # Executa alembic revision
    result = subprocess.run(
        ["alembic", "revision", "--autogenerate", "-m", migration_name],
        cwd=Path(__file__).resolve().parents[1]
    )

    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
