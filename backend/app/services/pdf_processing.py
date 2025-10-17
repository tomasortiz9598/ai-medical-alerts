"""Utilities for converting PDF files into text."""
from __future__ import annotations

import io
from pathlib import Path

from pdfminer.high_level import extract_text

try:
    import pytesseract  # type: ignore
    from pdf2image import convert_from_bytes  # type: ignore
except ImportError:  # pragma: no cover - optional dependencies
    pytesseract = None
    convert_from_bytes = None


class PDFExtractionError(RuntimeError):
    """Raised when a PDF cannot be processed."""


def extract_text_from_pdf(data: bytes, enable_ocr: bool = False) -> str:
    """Extract text from a PDF, optionally falling back to OCR."""

    with io.BytesIO(data) as buffer:
        text = extract_text(buffer)

    if text.strip():
        return text

    if enable_ocr and pytesseract and convert_from_bytes:
        images = convert_from_bytes(data)
        ocr_text = "\n".join(pytesseract.image_to_string(image) for image in images)
        if ocr_text.strip():
            return ocr_text

    raise PDFExtractionError("Unable to extract text from PDF. Consider enabling OCR dependencies.")


def extract_text_from_path(path: Path, enable_ocr: bool = False) -> str:
    with path.open("rb") as file:
        return extract_text_from_pdf(file.read(), enable_ocr=enable_ocr)
