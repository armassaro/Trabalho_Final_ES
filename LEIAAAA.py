"""
Lê o PDF, elimina todos os espaços em branco e separa cada questão em:
1. número          → int
2. enunciado       → str
3. pontos          → int
4. alternativas    → dict {'A':..., 'B':..., 'C':..., 'D':..., 'E':...}

Formato esperado (sem espaços):
(N)Pergunta(NPontos)(A).respA(B).respB(C).respC(D).respD(E).respE...
--------------------------------------------------------------------
"""

import re
from pathlib import Path
from PyPDF2 import PdfReader   # pip install PyPDF2

# ---------- CONFIGURAÇÃO ----------
PDF_PATH = Path("Teste.pdf")   # nome do arquivo na MESMA pasta do .py
# ----------------------------------

def extrair_texto_puro(pdf: Path) -> str:
    """Extrai texto do PDF e elimina TODOS os espaços em branco (tabs, \n, etc.)."""
    if not pdf.exists() or pdf.suffix.lower() != ".pdf":
        raise FileNotFoundError(f"Arquivo '{pdf}' não encontrado ou não é PDF")
    reader = PdfReader(str(pdf))
    bruto = "\n".join(page.extract_text() or "" for page in reader.pages)
    return re.sub(r"\s+", "", bruto)  # remove \s (espaço, tab, \r, \n, etc.)

def parse_questoes(texto: str):
    """
    Varre toda a string e devolve uma lista de dicts:
    [{'numero':1,'pontos':5,'pergunta':'...','alternativas':{'A':'...','B':'...'}}, ...]
    """
    padrao = re.compile(
        r"\((\d+)\)"            # (N)  → nº da questão
        r"(.*?)"                # Pergunta (lazy)
        r"\((\d+)Pontos\)"      # (NPontos)
        r"\(A\)\.?([^()]*?)"    # (A).respostaA
        r"\(B\)\.?([^()]*?)"    # (B).respostaB
        r"\(C\)\.?([^()]*?)"    # (C).respostaC
        r"\(D\)\.?([^()]*?)"    # (D).respostaD
        r"\(E\)\.?([^()]*?)"    # (E).respostaE
        r"(?=\(\d+\)|$)",       # pára antes da próxima questão ou do fim
        re.IGNORECASE | re.DOTALL
    )

    questoes = []
    for m in padrao.finditer(texto):
        numero   = int(m.group(1))
        enunciado= m.group(2)
        pontos   = int(m.group(3))
        # strip() remove pontinhos extras ou quebras acidentais
        alternativas = dict(zip("ABCDE",
            (resp.lstrip(".").strip() for resp in m.groups()[3:8])))

        questoes.append({
            "numero": numero,
            "pergunta": enunciado,
            "pontos": pontos,
            "alternativas": alternativas,
        })
    return questoes

# ----------------- EXECUÇÃO -----------------
conteudo_sem_espacos = extrair_texto_puro(PDF_PATH)
questions = parse_questoes(conteudo_sem_espacos)

# Exemplo de uso: imprimir tudo organizado
for q in questions:
    print(f"\nQuestão {q['numero']}  ({q['pontos']} pt)")
    print(q['pergunta'])
    for letra, resp in q['alternativas'].items():
        print(f"  {letra}) {resp}")
# --------------------------------------------
