"""
Utilitários para geração de QR Codes de licença.
"""
import io
import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer
from typing import Optional

from app.models import License


def generate_license_qrcode(
    license: License,
    size: int = 300,
    include_border: bool = True
) -> bytes:
    """
    Gera QR Code com o código da licença.

    Args:
        license: Instância de License
        size: Tamanho da imagem em pixels
        include_border: Se deve incluir borda

    Returns:
        Bytes da imagem PNG
    """
    # Dados para codificar
    # Inclui informações básicas para facilitar validação manual
    data = f"RFLEX:{license.code}"

    # Cria QR Code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4 if include_border else 0,
    )

    qr.add_data(data)
    qr.make(fit=True)

    # Cria imagem com estilo arredondado
    img = qr.make_image(
        fill_color="#1e40af",  # Azul corporativo
        back_color="white",
        image_factory=StyledPilImage,
        module_drawer=RoundedModuleDrawer()
    )

    # Redimensiona
    img = img.resize((size, size))

    # Converte para bytes
    buffer = io.BytesIO()
    img.save(buffer, format="PNG", optimize=True)
    buffer.seek(0)

    return buffer.read()


def generate_qrcode_base64(license: License, size: int = 300) -> str:
    """
    Gera QR Code e retorna como base64 (para uso em HTML).

    Args:
        license: Instância de License
        size: Tamanho da imagem

    Returns:
        String base64 da imagem
    """
    import base64

    img_bytes = generate_license_qrcode(license, size)

    return base64.b64encode(img_bytes).decode("utf-8")
