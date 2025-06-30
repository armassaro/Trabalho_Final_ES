import re
from pathlib import Path
from PyPDF2 import PdfReader

# Arquivo a ler
PDF_PATH = Path("novo.pdf")

# ────── Função que devolve TODO o texto do PDF ──────
def ler_pdf(pdf: Path) -> str:
    reader = PdfReader(str(pdf))
    # Junta texto de cada página em linhas diferentes
    return "\n".join(p.extract_text() or "" for p in reader.pages)

# ────── Regex para Nome / RA ──────
HEADER_RX = re.compile(
    r"Nome:\s*([A-Za-zÀ-ÿ ]+?)\s*RA:\s*(\d{7})",
    re.IGNORECASE | re.DOTALL
)

def parse_header(texto_bruto: str):
    """Extrai nome e RA; lança erro se não achar."""
    m = HEADER_RX.search(texto_bruto)
    if not m:
        raise ValueError("Cabeçalho (Nome / RA) não encontrado.")
    nome, ra = m.groups()
    return nome.strip(), ra

# ────── Regex que isola cada questão ──────
HEAD_RX = re.compile(
    r"\((\d+)\)"                 # (1) → grupo 1 (número)
    r"(.*?)"                     # enunciado (grupo 2)
    r"\((\d+)(?:Pontos|pts?)\)"  # (5Pontos) → grupo 3 (pontos)
    r"(.*?)"                     # corpo (grupo 4)
    r"(?=\(\d+\)|$)",            # look‑ahead: próxima questão ou fim
    re.DOTALL
)

# Regex para alternativas A‑E
ALT_RX = re.compile(
    r"([A-E])\(([^)]*)\)"  # letra + Boleano
    r"(.*?)"               # texto da alternativa
    r"(?=[A-E]\(|R:|$)",   # pára em próxima letra ou R: ou fim
    re.DOTALL
)

# Regex para resposta discursiva
RESP_RX = re.compile(r"R:([^A-E()]*)", re.DOTALL)

def parse_questoes(texto_compacto: str):
    """Retorna lista de dicionários representando as questões."""
    questoes = []

    for m in HEAD_RX.finditer(texto_compacto):
        num, enun, pts, corpo = m.groups()
        corpo = corpo.lstrip()

        # Caso 1: múltipla escolha
        if corpo.startswith("A"):
            alternativas = {
                letra: {
                    "Boleano": bool(Boleano.strip()),
                    "texto": texto.lstrip()
                }
                for letra, Boleano, texto in ALT_RX.findall(corpo)
            }
            questoes.append({
                "numero": int(num),
                "pergunta": enun,
                "pontos": int(pts),
                "alternativas": alternativas,
                "resposta": None
            })

        # Caso 2: discursiva
        elif corpo.startswith("R:"):
            m_resp = RESP_RX.match(corpo)
            resposta = m_resp.group(1).lstrip() if m_resp else ""
            questoes.append({
                "numero": int(num),
                "pergunta": enun,
                "pontos": int(pts),
                "alternativas": {},
                "resposta": resposta
            })

        # Formato inesperado
        else:
            raise ValueError(f"Formato inesperado na questão {num}")

    return questoes

# ────── Execução quando rodar diretamente ──────
if __name__ == "__main__":
    # Texto original
    texto_bruto = ler_pdf(PDF_PATH)

    # Cabeçalho
    nome_aluno, ra = parse_header(texto_bruto)
    print("Aluno :", nome_aluno)
    print("RA    :", ra)

    # Remove todos brancos p/ facilitar regex
    texto_sem_espacos = re.sub(r"\s+", "", texto_bruto)

    # Questões
    for q in parse_questoes(texto_sem_espacos):
        print(f"\nQuestão {q['numero']} ({q['pontos']} pt)")
        print(q['pergunta'])
        if q['resposta'] is not None:
            print(f"  [Discursiva] → {q['resposta']}")
        else:
            for l, d in q['alternativas'].items():
                print(f"  {l}) {d['texto']}   Boleano = {d['Boleano']}")
