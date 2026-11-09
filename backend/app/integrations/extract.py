"""Extract plain text from uploaded documents for knowledge-base indexing.

Text, PDF (text layer) and DOCX are extracted directly. Scanned images and
image-only PDFs use OCR (Tesseract) when it is installed; otherwise OCR is
skipped and an empty string is returned. OCR never raises — a missing binary or
an unreadable file degrades to "" so the caller reports "no extractable text".
"""

from __future__ import annotations

import io
import logging

from app.core.config import get_settings

logger = logging.getLogger(__name__)

TEXT_MIMES = {"text/plain", "text/markdown", "text/csv"}
PDF_MIMES = {"application/pdf"}
DOCX_MIMES = {
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}
IMAGE_EXTS = ("png", "jpg", "jpeg", "tif", "tiff", "bmp", "webp", "gif")

# If a PDF's text layer yields fewer characters than this, treat it as scanned
# and try OCR instead.
_PDF_TEXT_MIN = 40

_ocr_checked = False
_ocr_available = False


def _looks_like(name: str, *exts: str) -> bool:
    return bool(name) and name.lower().rsplit(".", 1)[-1] in exts


def extract_text(filename: str | None, mime: str | None, data: bytes) -> str:
    name = filename or ""
    mime = (mime or "").split(";")[0].strip().lower()

    if mime in TEXT_MIMES or _looks_like(name, "txt", "md", "csv"):
        return data.decode("utf-8", errors="replace")

    if mime in DOCX_MIMES or _looks_like(name, "docx"):
        return _extract_docx(data)

    if mime in PDF_MIMES or _looks_like(name, "pdf"):
        text = _extract_pdf(data)
        if len(text) < _PDF_TEXT_MIN and ocr_available():
            text = _ocr_pdf(data) or text
        return text

    if mime.startswith("image/") or _looks_like(name, *IMAGE_EXTS):
        return _ocr_image(data) if ocr_available() else ""

    return ""


def ocr_available() -> bool:
    """Whether the Tesseract binary is usable (cached)."""
    global _ocr_checked, _ocr_available
    if _ocr_checked:
        return _ocr_available
    _ocr_checked = True
    settings = get_settings()
    if not settings.ocr_enabled:
        _ocr_available = False
        return False
    try:
        import pytesseract

        if settings.tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = settings.tesseract_cmd
        pytesseract.get_tesseract_version()
        _ocr_available = True
    except Exception:
        logger.info("OCR disabled — Tesseract not available.")
        _ocr_available = False
    return _ocr_available


def _extract_pdf(data: bytes) -> str:
    try:
        from pypdf import PdfReader

        reader = PdfReader(io.BytesIO(data))
        parts = [(page.extract_text() or "") for page in reader.pages]
        return "\n\n".join(p.strip() for p in parts if p.strip())
    except Exception:
        return ""


def _extract_docx(data: bytes) -> str:
    try:
        import docx

        document = docx.Document(io.BytesIO(data))
        return "\n\n".join(p.text for p in document.paragraphs if p.text.strip())
    except Exception:
        return ""


def _ocr_image(data: bytes) -> str:
    try:
        import pytesseract
        from PIL import Image

        return pytesseract.image_to_string(Image.open(io.BytesIO(data))).strip()
    except Exception:
        return ""


def _ocr_pdf(data: bytes) -> str:
    try:
        import pytesseract
        from pdf2image import convert_from_bytes

        settings = get_settings()
        kwargs = {"poppler_path": settings.poppler_path} if settings.poppler_path else {}
        pages = convert_from_bytes(data, **kwargs)
        texts = [pytesseract.image_to_string(page).strip() for page in pages]
        return "\n\n".join(t for t in texts if t)
    except Exception:
        return ""
