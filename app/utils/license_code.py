"""
Utilitários para geração e validação de códigos de licença.
"""
import secrets
import string
from typing import Optional


def generate_license_code(length: int = 32) -> str:
    """
    Gera um código de licença único alfanumérico.

    O código é gerado usando criptografia segura (secrets module)
    para garantir aleatoriedade e evitar colisões.

    Args:
        length: Tamanho do código (padrão: 32 caracteres)

    Returns:
        Código de licença único (letras maiúsculas + números)
    """
    # Caracteres permitidos: A-Z e 0-9 (exclui I, O, 0, 1 para confusão visual)
    chars = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    return "".join(secrets.choice(chars) for _ in range(length))


def format_license_code(code: str, format_every: int = 4) -> str:
    """
    Formata o código da licença com hífens para facilitar leitura.

    Exemplo: ABCD-1234-EFGH-5678

    Args:
        code: Código da licença
        format_every: Adicionar hífen a cada N caracteres

    Returns:
        Código formatado
    """
    parts = [code[i:i + format_every] for i in range(0, len(code), format_every)]
    return "-".join(parts)


def validate_license_code_format(code: str) -> bool:
    """
    Valida se o código da licença tem o formato correto.

    Args:
        code: Código a ser validado

    Returns:
        True se o formato for válido
    """
    # Remove formatação
    clean_code = code.replace("-", "").replace(" ", "").upper()

    # Verifica tamanho
    if len(clean_code) != 32:
        return False

    # Verifica se é alfanumérico
    return all(c in "ABCDEFGHJKLMNPQRSTUVWXYZ23456789" for c in clean_code)


def sanitize_license_code(code: str) -> str:
    """
    Remove formatação e normaliza o código da licença.

    Args:
        code: Código possivelmente formatado

    Returns:
        Código limpo e em maiúsculas
    """
    return code.replace("-", "").replace(" ", "").upper()
