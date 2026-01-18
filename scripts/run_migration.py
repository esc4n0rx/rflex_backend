#!/usr/bin/env python3
"""
Script para executar migrations pendentes.

Uso:
    python scripts/run_migration.py
"""
import sys
from pathlib import Path

# Adiciona diretório raiz ao path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def main():
    """Executa migrations pendentes."""
    print("=" * 60)
    print("RFlex License Server - Executando Migrations")
    print("=" * 60)
    print()

    import subprocess

    # Executa alembic upgrade
    print("[*] Executando migrations...")
    result = subprocess.run(
        ["alembic", "upgrade", "head"],
        cwd=Path(__file__).resolve().parents[1]
    )

    if result.returncode == 0:
        print("[+] Migrations executadas com sucesso!")
    else:
        print("[!] Erro ao executar migrations.")

    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
