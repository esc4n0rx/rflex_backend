"""
Configurações da aplicação usando Pydantic Settings.
Todas as configurações sensíveis são carregadas de variáveis de ambiente.
"""
from functools import lru_cache
from typing import List, Union
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configurações centrais da aplicação."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Database
    db_host: str = Field(default="localhost", description="Host do banco de dados")
    db_port: int = Field(default=3306, description="Porta do banco de dados")
    db_name: str = Field(default="rflex_licenses", description="Nome do banco de dados")
    db_user: str = Field(default="root", description="Usuário do banco de dados")
    db_password: str = Field(default="", description="Senha do banco de dados")

    # API
    api_host: str = Field(default="0.0.0.0", description="Host da API")
    api_port: int = Field(default=8000, description="Porta da API")
    api_title: str = Field(default="RFlex License Server", description="Título da API")
    api_version: str = Field(default="1.0.0", description="Versão da API")
    environment: str = Field(default="development", description="Ambiente (development/production)")

    # Segurança
    secret_key: str = Field(default="", description="Chave secreta para JWT")
    algorithm: str = Field(default="HS256", description="Algoritmo de criptografia")
    access_token_expire_minutes: int = Field(
        default=480,
        description="Tempo de expiração do token de acesso (minutos)"
    )

    # Licenças
    grace_period_hours: int = Field(
        default=72,
        description="Período de tolerância offline (horas)"
    )
    default_license_validity_days: int = Field(
        default=30,
        description="Validade padrão da licença (dias)"
    )

    # CORS
    backend_cors_origins: Union[List[str], str] = Field(
        default=["https://www.rflex.sbs", "https://rflex.sbs"],
        description="Origens permitidas para CORS"
    )

    @field_validator("backend_cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            # Remove espaços e quebras de linha acidentais
            v = v.strip()
            if v.startswith("[") and v.endswith("]"):
                import json
                try:
                    return json.loads(v)
                except json.JSONDecodeError:
                    pass
            # Split por vírgula e limpa cada entrada
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    # Logging
    log_level: str = Field(default="INFO", description="Nível de log")
    log_file_path: str = Field(default="logs/rflex_backend.log", description="Caminho do arquivo de log")

    # Admin Master
    master_admin_email: str = Field(
        default="admin@rflex.com",
        description="Email do administrador master"
    )
    master_admin_password: str = Field(
        default="Admin@123456",
        description="Senha do administrador master"
    )

    @property
    def database_url(self) -> str:
        """URL de conexão do banco de dados."""
        return f"mysql+pymysql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}?charset=utf8mb4"


@lru_cache()
def get_settings() -> Settings:
    """
    Retorna instância cachada das configurações.
    Usar lru_cache garante que o arquivo .env seja lido apenas uma vez.
    """
    return Settings()


# Instância global das configurações
settings = get_settings()
