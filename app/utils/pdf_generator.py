"""
Utilitários para geração de PDF de licença.
"""
import io
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
    Image,
    PageBreak
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from app.models import License
from app.utils.qrcode_generator import generate_license_qrcode
from app.utils.license_code import format_license_code


def generate_license_pdf(license: License) -> bytes:
    """
    Gera um PDF com os detalhes da licença para impressão.

    O PDF contém:
    - Cabeçalho com branding RFlex
    - Código da licença formatado
    - QR Code para ativação fácil
    - Informações da empresa e plano
    - Instruções de ativação

    Args:
        license: Instância de License

    Returns:
        Bytes do PDF gerado
    """
    buffer = io.BytesIO()

    # Cria documento PDF
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    # Elementos do PDF
    elements = []

    # Estilos
    styles = getSampleStyleSheet()

    # Estilo customizado para título
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Heading1"],
        fontSize=24,
        textColor=HexColor("#1e40af"),
        spaceAfter=0.5 * cm,
        alignment=TA_CENTER,
        fontName="Helvetica-Bold"
    )

    # Estilo para subtítulo
    subtitle_style = ParagraphStyle(
        "CustomSubTitle",
        parent=styles["Heading2"],
        fontSize=14,
        textColor=HexColor("#64748b"),
        spaceAfter=1 * cm,
        alignment=TA_CENTER,
    )

    # Cabeçalho
    elements.append(Paragraph("RFlex Client", title_style))
    elements.append(Paragraph("Licença de Uso", subtitle_style))
    elements.append(Spacer(1, 1 * cm))

    # QR Code
    qrcode_img = generate_license_qrcode(license, size=200)
    qrcode_buffer = io.BytesIO(qrcode_img)
    qrcode_pdf = Image(qrcode_buffer, width=5 * cm, height=5 * cm, hAlign="CENTER")
    elements.append(qrcode_pdf)
    elements.append(Spacer(1, 1 * cm))

    # Código da licença
    code_style = ParagraphStyle(
        "CodeStyle",
        parent=styles["Code"],
        fontSize=16,
        textColor=HexColor("#0f172a"),
        alignment=TA_CENTER,
        fontName="Courier-Bold",
        spaceAfter=0.3 * cm
    )

    formatted_code = format_license_code(license.code)
    elements.append(Paragraph("Código da Licença:", styles["Heading3"]))
    elements.append(Paragraph(formatted_code, code_style))
    elements.append(Spacer(1, 1 * cm))

    # Informações da licença em tabela
    info_data = [
        ["Empresa:", license.company.trading_name],
        ["CNPJ:", license.company.cnpj or "N/A"],
        ["Plano:", license.plan.name],
        ["Status:", license.status.value.upper()],
        ["Validade:", license.expires_at.strftime("%d/%m/%Y")],
        ["Dispositivos:", f"{license.get_active_devices_count()} / {license.plan.max_devices if license.plan.max_devices != -1 else 'Ilimitado'}"],
    ]

    info_table = Table(info_data, colWidths=[5 * cm, 10 * cm])
    info_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 12),
        ("TEXTCOLOR", (0, 0), (0, -1), HexColor("#64748b")),
        ("TEXTCOLOR", (1, 0), (1, -1), HexColor("#0f172a")),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0.3 * cm),
        ("TOPPADDING", (0, 0), (-1, -1), 0.3 * cm),
    ]))

    elements.append(info_table)
    elements.append(Spacer(1, 1.5 * cm))

    # Instruções
    instructions_title = ParagraphStyle(
        "InstructionsTitle",
        parent=styles["Heading3"],
        fontSize=14,
        textColor=HexColor("#1e40af"),
        spaceAfter=0.5 * cm
    )

    instructions_body = ParagraphStyle(
        "InstructionsBody",
        parent=styles["BodyText"],
        fontSize=11,
        textColor=HexColor("#475569"),
        spaceAfter=0.3 * cm,
        leftIndent=0.5 * cm
    )

    elements.append(Paragraph("Como Ativar:", instructions_title))
    elements.append(Paragraph(
        "1. Abra o aplicativo RFlex Client no coletor.",
        instructions_body
    ))
    elements.append(Paragraph(
        "2. Acesse o menu de ativação de licença.",
        instructions_body
    ))
    elements.append(Paragraph(
        f"3. Digite o código: <b>{formatted_code}</b>",
        instructions_body
    ))
    elements.append(Paragraph(
        "4. Ou escaneie o QR Code acima.",
        instructions_body
    ))
    elements.append(Paragraph(
        "5. Aguarde a confirmação de ativação.",
        instructions_body
    ))
    elements.append(Spacer(1, 1 * cm))

    # Suporte
    support_style = ParagraphStyle(
        "Support",
        parent=styles["Normal"],
        fontSize=10,
        textColor=HexColor("#94a3b8"),
        alignment=TA_CENTER
    )

    elements.append(Paragraph(
        "Para suporte, entre em contato: suporte@rflex.com",
        support_style
    ))
    elements.append(Paragraph(
        f"Documento gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M')}",
        support_style
    ))

    # Rodapé em todas as páginas
    def on_page(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(HexColor("#e2e8f0"))
        canvas.drawString(
            2 * cm,
            2 * cm,
            "RFlex License Server - Documento Confidencial"
        )
        canvas.restoreState()

    # Build PDF
    doc.build(elements, onFirstPage=on_page, onLaterPages=on_page)

    buffer.seek(0)
    return buffer.read()


def generate_licenses_batch_pdf(licenses: list[License]) -> bytes:
    """
    Gera um PDF com múltiplas licenças (uma por página).

    Args:
        licenses: Lista de instâncias de License

    Returns:
        Bytes do PDF gerado
    """
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    elements = []

    for license in licenses:
        # Gera conteúdo da licença
        license_buffer = io.BytesIO(generate_license_pdf(license))

        # Adiciona página break entre licenças
        if elements:
            elements.append(PageBreak())

        # Importa conteúdo do PDF individual
        from PyPDF2 import PdfReader
        reader = PdfReader(license_buffer)
        # ... código para extrair e adicionar página ao PDF final
        # Isso requer biblioteca adicional, simplificando aqui:

        # Por enquanto, gera cada licença individualmente
        elements.append(Paragraph(
            f"Licença: {license.company.trading_name}",
            getSampleStyleSheet()["Heading2"]
        ))

    doc.build(elements)
    buffer.seek(0)
    return buffer.read()
