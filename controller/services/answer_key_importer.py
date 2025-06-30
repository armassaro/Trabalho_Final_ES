# controller/services/answer_key_importer.py
from pathlib import Path
from typing import Dict
from controller.parsers.answer_key_parser import AnswerKeyParser

class AnswerKeyImporter:
    """Fachada para ler o PDF de gabarito (alternativas corretas)."""

    def __init__(self, parser: AnswerKeyParser | None = None):
        self._parser = parser or AnswerKeyParser()

    def import_key(self, pdf_path: Path) -> Dict[int, str]:
        return self._parser.parse_pdf(pdf_path)
