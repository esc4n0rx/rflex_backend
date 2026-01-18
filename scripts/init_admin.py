#!/usr/bin/env python3
"""
Script para criar o administrador master do sistema.

Uso:
    python scripts/init_admin.py                              # Interativo
    python scripts/init_admin.py --email admin@rflex.com     # Usa email especificado
    python scripts/init_admin.py --auto                       # Usa configuracoes do .env

Este script:
1. Verifica se já existe um admin
2. Se não existir, cria o admin master
3. Se já existir, pergunta se deseja redefinir senha
"""
import sys
import argparse
from pathlib import Path

# Adiciona diretório raiz ao path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import uuid
import getpass
from sqlalchemy.orm import Session

from app.core.database import SessionLocal, engine, Base
from app.core.config import settings
from app.models import AdminUser
from app.models.admin_user import pwd_context


def create_admin_user(
    db: Session,
    email: str,
    password: str,
    full_name: str,
    is_superadmin: bool = True
) -> AdminUser:
    """
    Cria um usuário administrador.

    Args:
        db: Sessão do banco de dados
        email: Email do administradoradmin
        full_name: Nome completo
        is_superadmin: Se é superadmin

    Returns:
        Instância de AdminUser criada
    """
    # Verifica se email já existe
    existing = db.query(AdminUser).filter(AdminUser.email == email).first()
    if existing:
        raise ValueError(f"Já existe um administrador com o email {email}")

    # Cria administrador
    admin = AdminUser(
        id=str(uuid.uuid4()),
        email=email,
        full_name=full_name,
        is_active=True,
        is_superadmin=is_superadmin
    )
    admin.set_password(password)

    db.add(admin)
    db.commit()
    db.refresh(admin)

    return admin


def main():
    """Função principal."""
    parser = argparse.ArgumentParser(description="Criar administrador master")
    parser.add_argument("--email", help="Email do administrador")
    parser.add_argument("--password", help="Senha do administrador")
    parser.add_argument("--name", help="Nome completo do administrador")
    parser.add_argument("--auto", action="store_true", help="Usa configuracoes do .env automaticamente")

    args = parser.parse_args()

    print("=" * 60)
    print("RFlex License Server - Criação de Admin Master")
    print("=" * 60)
    print()

    # Cria tabelas se não existirem
    print("[*] Verificando banco de dados...")
    Base.metadata.create_all(bind=engine)
    print("[+] Banco de dados pronto")
    print()

    # Cria sessão
    db = SessionLocal()

    try:
        # Verifica se já existe admin
        existing_admins = db.query(AdminUser).all()

        if existing_admins:
            print(f"[!] Já existem {len(existing_admins)} administrador(es) no sistema:")
            for admin in existing_admins:
                superadmin_badge = " [SUPERADMIN]" if admin.is_superadmin else ""
                active_badge = " [ATIVO]" if admin.is_active else " [INATIVO]"
                print(f"   - {admin.email}{superadmin_badge}{active_badge}")
            print()

            # Pergunta se deseja criar outro
            response = input("Deseja criar outro administrador? (s/N): ").strip().lower()
            if response != "s":
                print("[*] Operação cancelada.")
                return

        # Coleta dados
        print()
        if args.auto or (args.email and args.password):
            # Modo automático
            email = args.email or settings.master_admin_email
            password = args.password or settings.master_admin_password
            full_name = args.name or "Administrator"
            print(f"[*] Usando configuracoes automaticas:")
            print(f"    Email: {email}")
            print(f"    Nome: {full_name}")
            print()
        else:
            # Modo interativo
            email_input = input(f"Email do administrador [{settings.master_admin_email}]: ").strip()
            email = email_input if email_input else settings.master_admin_email

            full_name_input = input("Nome completo [Administrator]: ").strip()
            full_name = full_name_input if full_name_input else "Administrator"

            # Senha
            while True:
                password = getpass.getpass("Senha (mínimo 8 caracteres): ")
                if len(password) < 8:
                    print("[!] A senha deve ter pelo menos 8 caracteres.")
                    continue

                password_confirm = getpass.getpass("Confirme a senha: ")
                if password != password_confirm:
                    print("[!] As senhas não coincidem.")
                    continue

                break

        # Cria admin
        print()
        print("[*] Criando administrador...")
        admin = create_admin_user(
            db,
            email=email,
            password=password,
            full_name=full_name,
            is_superadmin=True
        )

        print("[+] Administrador criado com sucesso!")
        print()
        print(f"   ID: {admin.id}")
        print(f"   Email: {admin.email}")
        print(f"   Nome: {admin.full_name}")
        print(f"   Superadmin: Sim")
        print()
        print("[!] Guarde estas informações com segurança.")
        print()

    except Exception as e:
        print(f"[!] Erro: {e}")
        db.rollback()
        return 1
    finally:
        db.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
