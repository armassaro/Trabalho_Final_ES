import re, sys
from pathlib import Path
from PyPDF2 import PdfReader

# ────────────────── util ──────────────────
def ler_pdf(pdf: Path) -> str:
    reader = PdfReader(str(pdf))
    return "\n".join(p.extract_text() or "" for p in reader.pages)

# ───────────────── HEADER ─────────────────
HEADER_RX = re.compile(
    r"Nome:\s*([A-Za-zÀ-ÿ ]+?)\s*RA:\s*(\d{7})",
    re.IGNORECASE | re.DOTALL
)

def parse_header(texto: str):
    m = HEADER_RX.search(texto)
    if not m:
        raise ValueError("Cabeçalho (Nome / RA) não encontrado.")
    return m.group(1).strip(), m.group(2)

# ────────── regex das questões ──────────
HEAD_RX = re.compile(
    r"\((\d+)\)(.*?)\((\d+)(?:Pontos|pts?)\)(.*?)"
    r"(?=\(\d+\)|$)", re.DOTALL
)

ALT_RX = re.compile(
    r"([A-E])\(([^)]*)\)(.*?)"
    r"(?=[A-E]\(|R:|$)", re.DOTALL
)

RESP_RX = re.compile(r"R:([^A-E()]*)", re.DOTALL)

def parse_questoes(texto: str):
    questoes = []
    for n, enun, pts, corpo in HEAD_RX.findall(texto):
        corpo = corpo.lstrip()
        if corpo.startswith("A"):                       # múltipla
            alternativas = {l: {"flag": bool(f.strip()),
                                 "texto": t.lstrip()}
                             for l, f, t in ALT_RX.findall(corpo)}
            questoes.append({"numero": int(n), "pergunta": enun,
                             "pontos": int(pts), "alternativas": alternativas,
                             "resposta": None})
        elif corpo.startswith("R:"):                    # discursiva
            resp = RESP_RX.match(corpo).group(1).lstrip()
            questoes.append({"numero": int(n), "pergunta": enun,
                             "pontos": int(pts), "alternativas": {},
                             "resposta": resp})
        else:
            raise ValueError(f"Formato inesperado na questão {n}")
    return questoes

# ───────────── MAIN ─────────────
if __name__ == "__main__":
    # 1⃣  Pega o caminho do PDF
    if len(sys.argv) == 2:
        pdf_path = Path(sys.argv[1]).expanduser()
    else:
        pdf_path = Path(input("Digite o caminho do PDF: ").strip('"')).expanduser()

    if not pdf_path.exists():
        sys.exit(f"❌ Arquivo '{pdf_path}' não encontrado.")

    # 2⃣  Lê texto bruto
    texto_bruto = ler_pdf(pdf_path)

    # 3⃣  Cabeçalho
    nome, ra = parse_header(texto_bruto)
    print(f"Aluno : {nome}")
    print(f"RA    : {ra}")

    # 4⃣  Remove espaços p/ regex das questões
    texto_compacto = re.sub(r"\s+", "", texto_bruto)

    # 5⃣  Questões
    for q in parse_questoes(texto_compacto):
        print(f"\nQuestão {q['numero']} ({q['pontos']} pt)")
        print(q['pergunta'])
        if q['resposta'] is None:
            for l, d in q['alternativas'].items():
                print(f"  {l}) {d['texto']}   flag={d['flag']}")
        else:
            print(f"  [Discursiva] → {q['resposta']}")
