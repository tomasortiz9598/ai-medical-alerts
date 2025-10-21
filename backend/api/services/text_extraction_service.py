import io

from pdf2image import convert_from_bytes
from pypdf import PdfReader
from pytesseract import image_to_string


class TextExtractionService:
    def extract_text_from_pdf(self, pdf_bytes: bytes) -> str:
        text_from_metadata = ""
        reader = PdfReader(io.BytesIO(pdf_bytes))
        images = convert_from_bytes(pdf_bytes, fmt="png")
        for i, _ in enumerate(reader.pages, start=1):
            text = reader.pages[i - 1].extract_text() or ""
            if len(text) < 10:
                text = image_to_string(images[i - 1])
            text_from_metadata += text
        return text_from_metadata


def get_text_extraction_service() -> TextExtractionService:
    return TextExtractionService()
