"""Extract plain text from uploaded documents for knowledge-base indexing.

Supports text, PDF (text-based) and DOCX. Scanned images / image-only PDFs need
OCR, which is deferred (returns empty text) — a later phase adds Tesseract.
"""

from __future__ import annotations

import io

TEXT_MIMES = {"text/plain", "text/markdown", "text/csv"}
PDF_MIMES = {"application/pdf"}
DOCX_MIMES = {
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}


def _looks_like(name: str, *exts: str) -> bool:
    return bool(name) and name.lower().rsplit(".", 1)[-1] in exts


def extract_text(filename: str | None, mime: str | None, data: bytes) -> str:
    """Return extracted text, or "" if the format is not text-extractable."""
    name = filename or ""
    mime = (mime or "").split(";")[0].strip().lower()

    if mime in TEXT_MIMES or _looks_like(name, "txt", "md", "csv"):
        return data.decode("utf-8", errors="replace")

    if mime in PDF_MIMES or _looks_like(name, "pdf"):
        return _extract_pdf(data)

    if mime in DOCX_MIMES or _looks_like(name, "docx"):
        return _extract_docx(data)

    return ""


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
