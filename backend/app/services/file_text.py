"""Extract plain text from uploaded files for exercise answers (code, notes, PDF, Word)."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path


def extract_text_from_upload(filename: str, data: bytes) -> tuple[str, str | None]:
    """
    Return (text, warning). Empty text with a warning means the file could not be usefully read.
    """
    name = (filename or "upload").strip() or "upload"
    ext = Path(name).suffix.lower()

    if not data:
        return "", "Empty file"

    if ext == ".pdf":
        try:
            from pypdf import PdfReader
        except ImportError:
            return "", "PDF support is not installed on the server"
        try:
            reader = PdfReader(BytesIO(data))
            chunks: list[str] = []
            for page in reader.pages:
                t = page.extract_text()
                if t:
                    chunks.append(t.strip())
            out = "\n\n".join(chunks).strip()
            if not out:
                return "", "No text extracted from PDF (scanned pages need OCR elsewhere)"
            return out, None
        except Exception as e:  # noqa: BLE001
            return "", f"Could not read PDF: {e!s}"

    if ext == ".docx":
        try:
            from docx import Document
        except ImportError:
            return "", "Word support is not installed on the server"
        try:
            doc = Document(BytesIO(data))
            paras = [p.text.strip() for p in doc.paragraphs if p.text and p.text.strip()]
            out = "\n".join(paras).strip()
            if not out:
                return "", "No paragraph text found in DOCX"
            return out, None
        except Exception as e:  # noqa: BLE001
            return "", f"Could not read DOCX: {e!s}"

    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        text = data.decode("utf-8", errors="replace")
        return text, "Non-UTF-8 bytes were replaced (file treated as text)"

    return text, None
