"""
Módulos de segurança: autenticação JWT, criptografia e autorização.
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models import AdminUser

# HTTP Bearer scheme para extração do token
security = HTTPBearer(auto_error=False)


def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Cria um token JWT de acesso.

    Args:
        data: Dados a serem codificados no token (geralmente {'sub': user_id})
        expires_delta: Delta de tempo para expiração (opcional)

    Returns:
        Token JWT codificado
    """
    to_encode = data.copy()

    # Define expiração
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.access_token_expire_minutes
        )

    to_encode.update({"exp": expire, "iat": datetime.utcnow()})

    # Codifica token
    encoded_jwt = jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.algorithm
    )

    return encoded_jwt


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decodifica e valida um token JWT.

    Args:
        token: Token JWT a ser decodificado

    Returns:
        Payload decodificado ou None se inválido
    """
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )
        return payload
    except JWTError:
        return None


def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> AdminUser:
    """
    Dependency para obter o administrador autenticado a partir do token.

    Args:
        credentials: Credenciais Bearer extraídas do header Authorization
        db: Sessão do banco de dados

    Returns:
        Instância de AdminUser autenticado

    Raises:
        HTTPException 401: Se token inválido, expirado ou usuário não encontrado
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Não foi fornecido credencial de autenticação",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials

    # Decodifica token
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Não foi possível validar as credenciais",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Extrai user_id
    user_id: str = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Não foi possível validar as credenciais",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Busca usuário no banco
    user = db.query(AdminUser).filter(AdminUser.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verifica se está ativo
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário inativo"
        )

    return user


def get_current_superadmin(
    current_admin: AdminUser = Depends(get_current_admin)
) -> AdminUser:
    """
    Dependency para obter o superadmin autenticado.

    Args:
        current_admin: Administrador autenticado

    Returns:
        Instância de AdminUser se for superadmin

    Raises:
        HTTPException 403: Se não for superadmin
    """
    if not current_admin.is_superadmin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado. Requer privilégios de superadmin"
        )
    return current_admin


class OptionalAuth:
    """
    Dependency para autenticação opcional.
    Tenta obter o usuário atual, mas retorna None se não houver token.
    """

    async def __call__(
        self,
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db: Session = Depends(get_db)
    ) -> Optional[AdminUser]:
        if credentials is None:
            return None

        token = credentials.credentials
        payload = decode_access_token(token)
        if payload is None:
            return None

        user_id = payload.get("sub")
        if user_id is None:
            return None

        user = db.query(AdminUser).filter(AdminUser.id == user_id).first()
        return user


# Instância para uso em rotas com autenticação opcional
optional_auth = OptionalAuth()


def create_device_token(device_id: str, license_id: str) -> str:
    """
    Cria um token JWT para um dispositivo (coletor).

    Este token é usado pelo app RFlex para validações periódicas.

    Args:
        device_id: ID do dispositivo
        license_id: ID da licença

    Returns:
        Token JWT codificado
    """
    data = {
        "sub": device_id,
        "type": "device",
        "license_id": license_id
    }

    # Token de dispositivo tem validade maior (90 dias)
    expire = datetime.utcnow() + timedelta(days=90)

    return create_access_token(data, timedelta(seconds=(expire - datetime.utcnow()).total_seconds()))


def verify_device_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decodifica e valida um token de dispositivo.

    Args:
        token: Token JWT do dispositivo

    Returns:
        Payload com device_id e license_id ou None se inválido
    """
    payload = decode_access_token(token)
    if payload is None:
        return None

    # Verifica se é token de dispositivo
    if payload.get("type") != "device":
        return None

    return {
        "device_id": payload.get("sub"),
        "license_id": payload.get("license_id")
    }
