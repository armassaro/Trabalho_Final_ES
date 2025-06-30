# Trabalho_Final_ES/models/dados_gabarito.py
import re
from PyPDF2 import PdfReader

# Regex necessário para extrair respostas de um PDF de gabarito
HEAD_RX = re.compile(
    r"\((\d+)\)(.*?)\((\d+(?:\.\d+)?)(?:Pontos|pts?)\)(.*?)"
    r"(?=\(\d+\)|$)", re.DOTALL
)
ALT_RX = re.compile(
    r"([A-E])\(([^)]*)\)(.*?)"
    r"(?=[A-E]\(|R:|$)", re.DOTALL
)
RESP_RX = re.compile(r"R:([^A-E()]*)", re.DOTALL)


class DadosGabarito:
    def __init__(self):
        self.dadosGabarito = []

    def lerGabarito(self, caminho_gabarito: str):
        # Lê um arquivo de gabarito. Suporta .txt ou um PDF de prova respondido.
        print(f"MODEL: Lendo o gabarito fornecido pelo usuário de '{caminho_gabarito}'...")
        self.dadosGabarito = []
        
        if caminho_gabarito.lower().endswith('.txt'):
            try:
                with open(caminho_gabarito, 'r', encoding='utf-8') as f:
                    for linha in f:
                        linha = linha.strip()
                        if ')' in linha:
                            # Formato esperado: "1) Resposta"
                            parts = linha.split(')', 1)
                            if len(parts) == 2:
                                self.dadosGabarito.append(parts[1].strip())
            except FileNotFoundError:
                print(f"MODEL: ERRO - Arquivo de gabarito não encontrado em '{caminho_gabarito}'")
            except Exception as e:
                print(f"MODEL: ERRO ao ler gabarito .txt: {e}")

        elif caminho_gabarito.lower().endswith('.pdf'):
            try:
                reader = PdfReader(caminho_gabarito)
                texto_bruto = "\n".join(p.extract_text() or "" for p in reader.pages)
            except Exception as e:
                texto_bruto = ""
                print(f"Erro ao ler o PDF '{caminho_gabarito}': {e}")
            
            if texto_bruto:
                texto_compacto = re.sub(r"\s+", "", texto_bruto)
                respostas = []
                for n, enun, pts, corpo in HEAD_RX.findall(texto_compacto):
                    corpo = corpo.lstrip()
                    if corpo.startswith("A"):
                        resposta_marcada = "N/A"
                        for letra, flag, texto in ALT_RX.findall(corpo):
                            if flag.strip():
                                resposta_marcada = letra
                                break
                        respostas.append(resposta_marcada)
                    elif corpo.startswith("R:"):
                        match = RESP_RX.match(corpo)
                        respostas.append(match.group(1).lstrip() if match else "")
                    else:
                        respostas.append("ERRO_FORMATO")
                self.dadosGabarito = respostas
        else:
            print(f"MODEL: ERRO - Formato de arquivo de gabarito não suportado: '{caminho_gabarito}'.")

        if self.dadosGabarito:
            print(f"MODEL: Gabarito lido com {len(self.dadosGabarito)} respostas.")