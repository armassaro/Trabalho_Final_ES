# controller/parsers/answer_key_parser.py
import re
from pathlib import Path
from typing import Dict
from PyPDF2 import PdfReader

class AnswerKeyParser:
    """
    Lê um PDF de gabarito no formato:
        1-A
        2-B
        3-C
    e devolve {1: "A", 2: "B", ...}
    """
    LINE_RX = re.compile(r"^\s*(\d+)\s*[-–]\s*([A-E])\s*$", re.I)

    def parse_pdf(self, pdf_path: Path) -> Dict[int, str]:
        reader = PdfReader(str(pdf_path))
        raw_text = "\n".join(p.extract_text() or "" for p in reader.pages)

        answer_key: Dict[int, str] = {}
        for line in raw_text.splitlines():
            m = self.LINE_RX.match(line)
            if m:
                num, letra = m.groups()
                answer_key[int(num)] = letra.upper()

        if not answer_key:
            raise ValueError("Nenhuma linha de gabarito encontrada.")

        return answer_key
