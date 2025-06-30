import re
from pathlib import Path
from PyPDF2 import PdfReader

PDF_PATH = Path("novo.pdf")          # ajuste se precisar

# ────────────────── util ──────────────────
def ler_pdf(pdf: Path) -> str:
    reader = PdfReader(str(pdf))
    return "\n".join(p.extract_text() or "" for p in reader.pages)

# ───────────────── HEADER ─────────────────
HEADER_RX = re.compile(
    r"Nome:\s*([A-Za-zÀ-ÿ ]+?)\s*RA:\s*(\d{7})",
    re.IGNORECASE | re.DOTALL
)

def parse_header(texto_bruto: str):
    m = HEADER_RX.search(texto_bruto)
    if not m:
        raise ValueError("Cabeçalho (Nome / RA) não encontrado.")
    nome, ra = m.groups()
    return nome.strip(), ra

# ────────── regex das questões ──────────
HEAD_RX = re.compile(
    r"\((\d+)\)"                 # (N)
    r"(.*?)"                     # enunciado
    r"\((\d+)(?:Pontos|pts?)\)"  # (NPontos)
    r"(.*?)"                     # corpo
    r"(?=\(\d+\)|$)",            # até próxima questão / fim
    re.DOTALL
)

ALT_RX = re.compile(
    r"([A-E])\(([^)]*)\)"        # letra + flag
    r"(.*?)"                     # texto até próxima alternativa / R: / fim
    r"(?=[A-E]\(|R:|$)",
    re.DOTALL
)

RESP_RX = re.compile(r"R:([^A-E()]*)", re.DOTALL)

# ────────── parser principal ──────────
def parse_questoes(texto_compacto: str):
    questoes = []

    for m in HEAD_RX.finditer(texto_compacto):
        num, enun, pts, corpo = m.groups()
        corpo = corpo.lstrip()

        if corpo.startswith("A"):                                 # múltipla‑escolha
            alternativas = {
                l: {"flag": bool(f.strip()), "texto": t.lstrip()}
                for l, f, t in ALT_RX.findall(corpo)
            }
            questoes.append({
                "numero": int(num),
                "pergunta": enun,
                "pontos": int(pts),
                "alternativas": alternativas,
                "resposta": None
            })
        elif corpo.startswith("R:"):                              # discursiva
            m_resp = RESP_RX.match(corpo)
            resposta = m_resp.group(1).lstrip() if m_resp else ""
            questoes.append({
                "numero": int(num),
                "pergunta": enun,
                "pontos": int(pts),
                "alternativas": {},
                "resposta": resposta
            })
        else:
            raise ValueError(f"Formato inesperado após pontos na questão {num}")

    return questoes

# ───────────── demo de uso ─────────────
if __name__ == "__main__":
    texto_bruto = ler_pdf(PDF_PATH)

    # 1) Cabeçalho
    nome_aluno, ra = parse_header(texto_bruto)
    print("Aluno :", nome_aluno)
    print("RA    :", ra)

    # 2) Compacta para remover todos os espaços em branco
    texto_sem_espacos = re.sub(r"\s+", "", texto_bruto)

    # 3) Questões
    for q in parse_questoes(texto_sem_espacos):
        print(f"\nQuestão {q['numero']} ({q['pontos']} pt)")
        print(q['pergunta'])
        if q['resposta'] is not None:
            print(f"  [Discursiva] → {q['resposta']}")
        else:
            for l, d in q['alternativas'].items():
                print(f"  {l}) {d['texto']}   flag={d['flag']}")
