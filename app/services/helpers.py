"""
Shared helpers for paperwork generation services.
"""

import logging
import random
import re
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from ..config import get_settings

logger = logging.getLogger("paperworkgen.services.helpers")
settings = get_settings()


def get_week_end_from_date(date: datetime) -> datetime:
    """Return the Sunday that ends the week containing the provided date."""
    days_to_sunday = 6 - date.weekday()
    return date + timedelta(days=days_to_sunday)


def format_date_for_cell(date: datetime) -> str:
    """Format a datetime for insertion into Excel cells."""
    return date.strftime("%A %d/%m/%y")


def format_folder_date(date: datetime) -> str:
    """Format a datetime for folder naming (DD-MM-YY)."""
    return date.strftime("%d-%m-%y")


def ensure_output_folder(date: datetime) -> Path:
    """Ensure the paperwork output folder exists for the target week."""
    folder = settings.output_dir / format_folder_date(date)
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def sanitize_filename(value: str) -> str:
    """Produce a filesystem-safe filename from descriptive text."""
    cleaned = re.sub(r"[^A-Za-z0-9-_\.]+", "_", value.strip())
    cleaned = cleaned.strip("_.-")
    return cleaned or "paperwork"


def _random_signature(signature_dir: Path) -> Optional[Path]:
    if not signature_dir.exists():
        return None
    candidates = [
        path for path in signature_dir.iterdir()
        if path.suffix.lower() in {".png", ".jpg", ".jpeg"}
    ]
    if not candidates:
        return None
    return random.choice(candidates)


def select_signature(requested: str, signature_dir: Path) -> Optional[Path]:
    """Resolve a signature path, honoring 'random' requests."""
    if requested == "random":
        return _random_signature(signature_dir)
    if requested:
        path = Path(requested)
        if path.exists():
            return path
    return None


def add_signature(worksheet, signature_path: Optional[Path], cell: str) -> None:
    """Insert a signature image into a worksheet cell."""
    if not signature_path or not signature_path.exists():
        return
    try:
        from openpyxl.drawing.image import Image as OpenpyxlImage

        image = OpenpyxlImage(str(signature_path))
        image.anchor = cell
        worksheet.add_image(image)
    except Exception as exc:
        logger.warning("Unable to embed signature %s: %s", signature_path, exc)


def convert_excel_to_pdf(excel_path: Path, output_dir: Path) -> Optional[Path]:
    """Run LibreOffice to convert the workbook to PDF."""
    if not settings.pdf_enabled:
        logger.debug("PDF conversion disabled; skipping LibreOffice")
        return None
    if not excel_path.exists():
        logger.warning("Excel file %s missing, cannot convert to PDF", excel_path)
        return None
    try:
        cmd = [
            "libreoffice",
            "--headless",
            "--convert-to",
            "pdf",
            "--outdir",
            str(output_dir),
            str(excel_path),
        ]
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=settings.libreoffice_timeout
        )
        if result.returncode != 0:
            logger.warning(
                "LibreOffice returned %s: %s",
                result.returncode,
                result.stderr.strip(),
            )
            return None
    except (FileNotFoundError, subprocess.SubprocessError) as exc:
        logger.warning("LibreOffice conversion failed: %s", exc)
        return None

    pdf_path = output_dir / f"{excel_path.stem}.pdf"
    return pdf_path if pdf_path.exists() else None
