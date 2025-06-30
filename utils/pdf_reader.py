# utils/pdf_reader.py
from pathlib import Path
from PyPDF2 import PdfReader

def read_pdf(path: Path) -> str:
    """Devolve o texto pesquisável de todas as páginas do PDF."""
    reader = PdfReader(str(path))
    return "\n".join(p.extract_text() or "" for p in reader.pages)
