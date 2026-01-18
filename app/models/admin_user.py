"""
Modelo de usuário administrador.
"""
import uuid
from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import relationship
from passlib.context import CryptContext

from app.models.base import BaseModel

# Contexto de criptografia de senha
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AdminUser(BaseModel):
    """
    Usuário administrador do sistema.

    Atributos:
        id: Identificador único
        email: Email de login (único)
        hashed_password: Senha criptografada com bcrypt
        full_name: Nome completo do administrador
        is_active: Se o usuário está ativo
        is_superadmin: Se é superadmin (acesso total)
    """
    __tablename__ = "admin_users"

    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        comment="ID único do administrador"
    )
    email = Column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
        comment="Email de login (único)"
    )
    hashed_password = Column(
        String(255),
        nullable=False,
        comment="Senha criptografada (bcrypt)"
    )
    full_name = Column(
        String(255),
        nullable=False,
        comment="Nome completo do administrador"
    )
    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="Se o usuário está ativo"
    )
    is_superadmin = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="Se é superadmin (acesso total irrestrito)"
    )

    def verify_password(self, password: str) -> bool:
        """
        Verifica se a senha fornecida corresponde à senha armazenada.

        Args:
            password: Senha em texto plano

        Returns:
            True se a senha estiver correta
        """
        return pwd_context.verify(password, self.hashed_password)

    def set_password(self, password: str) -> None:
        """
        Define a senha do usuário (criptografa antes de armazenar).

        Args:
            password: Senha em texto plano
        """
        # Bcrypt tem limite de 72 bytes
        if len(password.encode('utf-8')) > 72:
            password = password.encode('utf-8')[:72].decode('utf-8', errors='ignore')
        self.hashed_password = pwd_context.hash(password)

    @classmethod
    def create_password_hash(cls, password: str) -> str:
        """
        Cria um hash de senha (para testes e criação inicial).

        Args:
            password: Senha em texto plano

        Returns:
            Hash da senha
        """
        return pwd_context.hash(password)
