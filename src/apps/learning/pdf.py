from datetime import date
from decimal import Decimal

from .models import Certificate


def _pdf_literal(value: str) -> str:
    data = value.encode("cp1252", errors="replace")
    chunks = []
    for byte in data:
        character = chr(byte)
        if 32 <= byte <= 126 and character not in {"\\", "(", ")"}:
            chunks.append(character)
        else:
            chunks.append(f"\\{byte:03o}")
    return "(" + "".join(chunks) + ")"


def _centered_text(value: str, *, y: int, size: int, font: str = "F1") -> str:
    estimated_width = len(value) * size * 0.48
    x = max(48, int((842 - estimated_width) / 2))
    return f"BT /{font} {size} Tf 1 0 0 1 {x} {y} Tm {_pdf_literal(value)} Tj ET"


def _format_date(value: date) -> str:
    return value.strftime("%d/%m/%Y")


def _format_workload(value: Decimal) -> str:
    return f"{value:.2f}".replace(".", ",")


def render_certificate_pdf(certificate: Certificate) -> bytes:
    enrollment = certificate.enrollment
    class_group = enrollment.class_group
    participant_name = enrollment.participant.full_name
    title_size = 27 if len(participant_name) <= 45 else 20

    stream_lines = [
        "q 0.071 0.306 0.471 RG 3 w 28 28 786 539 re S Q",
        "q 0.957 0.725 0.259 rg 28 510 786 57 re f Q",
        _centered_text("CÓDIGO DO FUTURO", y=535, size=18, font="F2"),
        _centered_text("CERTIFICADO DE CONCLUSÃO", y=455, size=25, font="F2"),
        _centered_text("Certificamos que", y=408, size=13),
        _centered_text(participant_name, y=360, size=title_size, font="F2"),
        _centered_text(
            f"concluiu com aprovação a oficina {class_group.workshop.title}",
            y=315,
            size=14,
        ),
        _centered_text(
            f"Turma {class_group.code} — período de "
            f"{_format_date(class_group.start_date)} a {_format_date(class_group.end_date)}",
            y=280,
            size=12,
        ),
        _centered_text(
            f"Carga horária realizada: {_format_workload(certificate.workload_hours)} horas",
            y=245,
            size=12,
        ),
        _centered_text(
            f"Emitido em {_format_date(certificate.issued_at.date())}",
            y=188,
            size=11,
        ),
        _centered_text(
            f"Código de identificação: {certificate.verification_code}",
            y=105,
            size=10,
            font="F2",
        ),
        _centered_text(
            "Documento emitido pela Plataforma Código do Futuro",
            y=76,
            size=9,
        ),
    ]
    stream = "\n".join(stream_lines).encode("ascii")

    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        (
            b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 842 595] "
            b"/Resources << /Font << /F1 4 0 R /F2 5 0 R >> >> "
            b"/Contents 6 0 R >>"
        ),
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold "
        b"/Encoding /WinAnsiEncoding >>",
        b"<< /Length " + str(len(stream)).encode("ascii") + b" >>\nstream\n"
        + stream
        + b"\nendstream",
    ]

    document = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = [0]
    for number, obj in enumerate(objects, start=1):
        offsets.append(len(document))
        document.extend(f"{number} 0 obj\n".encode())
        document.extend(obj)
        document.extend(b"\nendobj\n")

    xref_offset = len(document)
    document.extend(f"xref\n0 {len(objects) + 1}\n".encode())
    document.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        document.extend(f"{offset:010d} 00000 n \n".encode())
    document.extend(
        (
            f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
            f"startxref\n{xref_offset}\n%%EOF\n"
        ).encode()
    )
    return bytes(document)
