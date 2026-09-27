"""Input helpers for plain text and text-based PDF documents."""

from pathlib import Path

from pypdf import PdfReader


def read_document(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Document not found: {path}")

    if path.suffix.casefold() == ".pdf":
        # pypdf reads an existing text layer. Image-only scans need OCR upstream.
        pages = [page.extract_text() or "" for page in PdfReader(path).pages]
        text = "\n\n".join(pages).strip()
        if not text:
            raise ValueError("The PDF contains no extractable text; OCR is required.")
        return text

    return path.read_text(encoding="utf-8")
