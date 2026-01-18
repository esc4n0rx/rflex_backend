"""
Rotas de autenticação de administradores.
"""
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import create_access_token, get_current_admin
from app.core.config import settings
from app.models import AdminUser
from app.schemas import AdminLogin, Token, AdminUserResponse

router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.post("/login", response_model=Token)
def login(
    credentials: AdminLogin,
    db: Session = Depends(get_db)
):
    """
    Realiza login de administrador.

    Args:
        credentials: Email e senha
        db: Sessão do banco de dados

    Returns:
        Token de acesso JWT

    Raises:
        HTTPException 401: Se credenciais inválidas
    """
    # Busca usuário por email
    user = db.query(AdminUser).filter(
        AdminUser.email == credentials.email
    ).first()

    # Verifica se existe e senha está correta
    if not user or not user.verify_password(credentials.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verifica se está ativo
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário inativo"
        )

    # Cria token de acesso
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes)
    )

    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60
    )


@router.get("/me", response_model=AdminUserResponse)
def get_current_user(
    current_admin: AdminUser = Depends(get_current_admin)
):
    """
    Retorna informações do administrador autenticado.

    Args:
        current_admin: Administrador autenticado (via dependency)

    Returns:
        Dados do administrador
    """
    return current_admin


@router.post("/logout")
def logout():
    """
    Faz logout do administrador.

    Como usamos JWT stateless, o logout é gerenciado pelo cliente
    removendo o token armazenado.
    """
    return {"message": "Logout realizado com sucesso. Remova o token do cliente."}
