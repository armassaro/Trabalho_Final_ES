# services/quiz_importer.py
from pathlib import Path
from typing import Dict
from utils.pdf_reader import read_pdf 
from parsers.base_parser import BaseParser

class QuizImporter:
    """
    Fachada: oferece apenas parse_pdf(), escondendo leitura e estratégia.
    Controller interage SOMENTE com essa classe.
    """

    def __init__(self, parser: BaseParser):
        self._parser = parser  # Strategy injetada

    def parse_pdf(self, pdf_path: Path) -> Dict:
        raw = read_pdf(pdf_path)
        return self._parser.parse(raw)
