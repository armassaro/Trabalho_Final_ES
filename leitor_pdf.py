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
    r"\(\s*(\d+)\s*\)\s*(.*?)\s*\(\s*(\d+(?:\.\d+)?)\s*(?:Pontos|pts?)\s*\)(.*?)(?=\(\s*\d+\s*\)|$)",
    re.DOTALL | re.IGNORECASE
)

ALT_RX = re.compile(
    r"([A-E])\s*\(([^)]*)\)\s*(.*?)(?=\s*[A-E]\s*\(|\s*R:|$)",
    re.DOTALL | re.IGNORECASE
)

# O RESP_RX não é mais necessário, a extração será feita de forma mais simples.

def parse_questoes(texto: str):
    # Esta função agora recebe o texto bruto, com espaços.
    questoes = []
    for n, enun, pts, corpo in HEAD_RX.findall(texto):
        # O 'corpo' da questão é verificado para saber o tipo de questão
        if corpo.lower().startswith("a"):  # Múltipla escolha
            alternativas = {
                letra: {"flag": bool(flag.strip()), "texto": texto.strip()}
                for letra, flag, texto in ALT_RX.findall(corpo)
            }
            questoes.append({
                "numero": int(n),
                "pergunta": enun,
                "pontos": int(float(pts)),
                "alternativas": alternativas,
                "resposta": None
            })
        elif corpo.lower().startswith("r:"):  # Discursiva
            # A resposta é extraída diretamente do corpo, removendo o "R:"
            resp = corpo[2:].strip()
            questoes.append({
                "numero": int(n),
                "pergunta": enun,
                "pontos": int(float(pts)),
                "alternativas": {},
                "resposta": resp
            })
        else:
            # Se não encontrar 'A)' ou 'R:', pode ser uma questão mal formatada.
            # Mesmo assim, tentamos salvar a pergunta.
             questoes.append({
                "numero": int(n),
                "pergunta": enun,
                "pontos": int(float(pts)),
                "alternativas": {},
                "resposta": f"[Formato inesperado no corpo da questão: {corpo}]"
            })
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
    try:
        nome, ra = parse_header(texto_bruto)
        print(f"Aluno : {nome}")
        print(f"RA    : {ra}")
    except ValueError as e:
        print(e)
    
    # 4⃣  CORREÇÃO: A linha que removia os espaços foi deletada.
    # texto_compacto = re.sub(r"\s+", "", texto_bruto)

    # 5⃣  Questões
    # A função agora usa o texto_bruto, preservando os espaços.
    questoes_parsed = parse_questoes(texto_bruto)
    if not questoes_parsed:
        print("\nNenhuma questão encontrada no formato esperado.")
        
    for q in questoes_parsed:
        print(f"\nQuestão {q['numero']} ({q['pontos']} pt)")
        print(q['pergunta'])
        if q['resposta'] is None:
            for l, d in q['alternativas'].items():
                print(f"  {l}) {d['texto']}   (Marcada: {d['flag']})")
        else:
            print(f"  [Discursiva] → {q['resposta']}")