from __future__ import annotations

import hashlib
import os
import uuid
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Any

import pandas as pd
from django.core.files.base import ContentFile
from django.utils.timezone import now
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Image,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from app.config.core.models import dttotDocReport

# Constants for the official letterhead
OFFICIAL_ADDRESS = """
PT Dana Saham Bersama
Roxy Square Lt.1
Jl. Kyai Tapa no.1
RT.10 RW.10
Tomang
Kec.Grogol Petamburan
Kota Jakarta Barat
Daerah Khusus Ibukota Jakarta 11440
"""

OFFICIAL_CONTACT = """
Telp. (021) 56954551
Whatsapp. 088290730739
Email. cs@danasaham.co.id
"""

OFFICIAL_LOGO = Path(__file__).parent.parent / "static" / "logo_danasaham.png"
LETTER_TITLE_RESULTS = """
Laporan Penerapan Program Anti Pencucian Uang
Pencegahan Pendanaan Terorisme,
dan Pencegahan Pendanaan Proliferasi Senjata Pemusnah Massal
Sektor Jasa Keuangan
"""

def encrypt_dttotdoc_report(filename: str) -> str:
    """Use SHA-256 to hash the filename and preserve the original file extension."""
    sha256_hash = hashlib.sha256()
    sha256_hash.update(filename.encode("utf-8"))
    encrypted_filename = sha256_hash.hexdigest()
    file_extension = os.path.splitext(filename)[1]  # noqa: PTH122
    return encrypted_filename + file_extension

def dttotdoc_report_directory_path(instance: Any, filename: str) -> str:
    """Generate a path to store an uploaded file."""
    date_now = instance.created_date or now()
    return "{app_name}/{dttotdoc_report_id}/{year}/{month}/{day}/{filename}".format(  # noqa: UP032
        app_name=instance._meta.app_label,  # noqa: SLF001
        dttotdoc_report_id=instance.dttotdoc_report,
        year=date_now.year,
        month=date_now.month,
        day=date_now.day,
        filename=encrypt_dttotdoc_report(filename),
    )

def save_generated_report_file(
        instance: Any,
        file_content: bytes,
        file_extension: str,
) -> None:
    """Save the generated report file to the instance."""
    if file_content:
        filename = f"{instance.dttotdoc_report.dttotdoc_report_id}{file_extension}"
        encrypted_filename = encrypt_dttotdoc_report(filename)
        file_path = dttotdoc_report_directory_path(instance, encrypted_filename)

        content_file = ContentFile(file_content, name=os.path.basename(file_path))  # noqa: PTH119
        instance.document_file.save(content_file.name, content_file, save=False)


def generate_letter_reference() -> str:
    """Generate an automatic letter reference number."""
    today = datetime.today()  # noqa: DTZ002
    return f"LT-{today.strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"


def get_dynamic_content(report: dttotDocReport) -> str:  # noqa: ARG001
    """Generate the dynamic content for the letter body.

    Args:
    ----
        report (dttotDocReport): The DTTOT report document to generate content for.

    Returns:
    -------
        str: The generated dynamic content for the letter body.

    """
    # Get today's date
    today_date = datetime.today()  # noqa: DTZ002

    # Get day, month, year, and time strings
    day_name = today_date.strftime("%A")
    day = today_date.day
    month = today_date.strftime("%B")
    year = today_date.year
    time = today_date.strftime("%H:%M:%S")

    # Generate the dynamic content
    return f"""
    Pada hari ini, {day_name} - {day}
    tanggal {day},
    bulan {month},
    tahun {year},
    Pukul {time}

    Telah dilakukan pengecekan dan pencocokan data seluruh nasabah Danasaham yang terdaftar sampai per {today_date.strftime('%Y-%m-%d')} dengan data Daftar Terduga Teroris dan Organisasi Teroris (DTTOT).
    Pengecekan dan pencocokan menggunakan alat bantu yaitu Sistem Internal Pengecekan dan Pelaporan Danasaham yang menjadi satu bagian dengan Sistem Manajemen Sumber Daya Perusahaan yang terintegrasi.
    Hasilnya, ditemukan {dttotDocReport.objects.filter(created_date__lte=today_date).count()} dengan rerata kecocokan diatas {dttotDocReport.objects.filter(created_date__lte=today_date).aggregate(median_score=pd.Series.median('score_match_similarity'))['median_score']}.
    Terlampir detail nasabah yang memiliki kecocokan dengan data Daftar Teroris dan Organisasi Teroris.
    Demikian laporan ini disampaikan.

    Atas perhatiannya, kami mengucapkan terima kasih.
    """

def generate_pdf_report(report: dttotDocReport) -> bytes:
    """Generate a PDF report for the DTTOT Report document."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    elements = []

    # Add logo
    if OFFICIAL_LOGO.exists():
        logo = Image(str(OFFICIAL_LOGO), 3 * inch, 2 * inch)
        elements.append(logo)
        elements.append(Spacer(1, 12))

    # Add Address
    address = Paragraph(OFFICIAL_ADDRESS, getSampleStyleSheet()["Normal"])
    elements.append(address)
    elements.append(Spacer(1, 12))

    # Add Contact
    contact = Paragraph(OFFICIAL_CONTACT, getSampleStyleSheet()["Normal"])
    elements.append(contact)
    elements.append(Spacer(1, 12))

    # Add title
    title = Paragraph(LETTER_TITLE_RESULTS, getSampleStyleSheet()["Title"])
    elements.append(title)
    elements.append(Spacer(1, 12))

    # Add Letter Reference
    letter_reference = Paragraph(f"Reference Number: {generate_letter_reference()}", getSampleStyleSheet()["Normal"])
    elements.append(letter_reference)
    elements.append(Spacer(1, 12))

    # Add dynamic content
    dynamic_content = Paragraph(get_dynamic_content(report), getSampleStyleSheet()["Normal"])
    elements.append(dynamic_content)
    elements.append(Spacer(1, 12))

    # Table with dttotDocReport data
    data = [
        ["Report ID", "Personal", "Created Date", "DTTOT ID", "Similarity Score"],
        [str(report.dttotdoc_report_id), str(report.dttotdoc_report_personal), report.created_date.strftime("%Y-%m-%d %H:%M:%S"), str(report.dttot_id), f"{report.score_match_similarity:.2f}"],
    ]

    if report:
        data.append([
            str(report.dttotdoc_report_id),
            str(report.dttotdoc_report_personal),
            report.created_date.strftime("%Y-%m-%d %H:%M:%S"),
            str(report.dttot_id),
            f"{report.score_match_similarity:.2f}",
        ])
    else:
        data.append(["", "", "", "", ""])

    table = Table(data)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 12),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
        ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 12))

    # Digital Signature Placeholder
    signature_paragraph = Paragraph("Digital Signature: ___________________", getSampleStyleSheet()["Normal"])
    elements.append(signature_paragraph)

    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    return pdf

def generate_csv_report(report: dttotDocReport) -> bytes:
    """Generate a CSV report for the DTTOT Report document."""
    buffer = BytesIO()
    data = {
        "Report ID": [str(report.dttotdoc_report_id)],
        "Personal ID": [str(report.dttotdoc_report_personal)],
        "Created Date": [report.created_date.strftime("%Y-%m-%d %H:%M:%S")],
        "DTTOT ID": [str(report.dttot_id)],
        "Similarity Score": [f"{report.score_match_similarity:.2f}"],
    }
    df = pd.DataFrame(data)  # noqa: PD901
    df.to_csv(buffer, index=False)
    buffer.seek(0)
    return buffer.getvalue()
