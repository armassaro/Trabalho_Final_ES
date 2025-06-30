# parsers/default_parser.py
import re
from typing import Dict, List
from .base_parser import BaseParser

class DefaultParser(BaseParser):
    """Parser padrão para provas: Nome/RA + questões A‑E ou R:."""

    # Regex pré‑compilados
    HEADER_RX = re.compile(r"Nome:\s*([A-Za-zÀ-ÿ ]+?)\s*RA:\s*(\d{7})",
                           re.I | re.S)
    Q_BLOCK_RX = re.compile(
        r"\(\s*(\d+)\s*\)"                        # número
        r"\s*(.*?)\s*"                            # enunciado
        r"\(\s*(\d+(?:\.\d+)?)\s*(?:Pontos|pts?)\s*\)"  # pontos
        r"(.*?)"                                  # corpo
        r"(?=\(\s*\d+\s*\)|$)",                   # próxima questão ou fim
        re.I | re.S
    )
    ALT_RX = re.compile(
        r"([A-E])\s*\(([^)]*)\)\s*"               # letra + flag
        r"(.*?)"                                  # texto
        r"(?=\s*[A-E]\s*\(|\s*R:|$)",             # look‑ahead
        re.I | re.S
    )

    def parse(self, raw_text: str) -> Dict:
        # 1) Cabeçalho
        m = self.HEADER_RX.search(raw_text)
        if not m:
            raise ValueError("Cabeçalho Nome/RA não encontrado.")
        nome, ra = m.groups()

        # 2) Questões
        questoes: List[Dict] = []
        for num, enun, pts, corpo in self.Q_BLOCK_RX.findall(raw_text):
            corpo = corpo.lstrip()
            if corpo.lower().startswith("a"):        # múltipla‑escolha
                alts = {l: {"flag": bool(f.strip()),
                             "texto": t.strip()}
                        for l, f, t in self.ALT_RX.findall(corpo)}
                questoes.append({"numero": int(num),
                                 "pergunta": enun.strip(),
                                 "pontos": int(float(pts)),
                                 "alternativas": alts,
                                 "resposta": None})
            elif corpo.lower().startswith("r:"):     # discursiva
                questoes.append({"numero": int(num),
                                 "pergunta": enun.strip(),
                                 "pontos": int(float(pts)),
                                 "alternativas": {},
                                 "resposta": corpo[2:].strip()})
            else:
                questoes.append({"numero": int(num),
                                 "pergunta": enun.strip(),
                                 "pontos": int(float(pts)),
                                 "alternativas": {},
                                 "resposta": f"[formato inesperado: {corpo[:30]}...]"})
        return {"nome": nome.strip(),
                "ra": ra,
                "questoes": questoes}
