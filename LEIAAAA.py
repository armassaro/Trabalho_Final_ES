"""
Extrai todo o texto de um PDF para uma string
--------------------------------------------
• 1) Instalar PyPDF2  (pip install PyPDF2) 
• 2) Altere a variável PDF_PATH com o nome do seu arquivo
"""

from pathlib import Path
from PyPDF2 import PdfReader   # pip install PyPDF2

# 1) Informe o nome (ou caminho) do PDF
PDF_PATH = Path("Teste2.pdf")      # Se estiver na mesma pasta do .py basta o nome

# ------------------------------------------------------------------------
def extrair_texto(pdf: Path) -> str:
    """Lê todas as páginas e devolve o texto como uma única string."""
    if not pdf.exists() or pdf.suffix.lower() != ".pdf":
        raise FileNotFoundError(f"Arquivo '{pdf}' não encontrado ou não é PDF")
    
    reader = PdfReader(str(pdf))
    return "\n".join(page.extract_text() or "" for page in reader.pages)

# 2) Executa
conteudo_pdf = extrair_texto(PDF_PATH)

# 3) Exibe a string
print("==== INÍCIO DO TEXTO EXTRAÍDO ====\n")
print(conteudo_pdf)
print("\n==== FIM ====")
