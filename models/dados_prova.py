# Trabalho_Final_ES/models/dados_prova.py
import re
from PyPDF2 import PdfReader

# Regex para extrair a estrutura das questões do PDF
HEAD_RX = re.compile(
    r"\((\d+)\)(.*?)\((\d+(?:\.\d+)?)(?:Pontos|pts?)\)(.*?)"
    r"(?=\(\d+\)|$)", re.DOTALL
)
ALT_RX = re.compile(
    r"([A-E])\(([^)]*)\)(.*?)"
    r"(?=[A-E]\(|R:|$)", re.DOTALL
)

class DadosProva:
    def __init__(self):
        self.dadosProva = []

    def lerProva(self, prova_path: str):
        # Lê a estrutura da prova a partir de um arquivo PDF modelo,
        # usando o parser integrado.
        print(f"MODEL: Lendo a estrutura da prova de '{prova_path}'...")
        self.dadosProva = [] 
        
        # Lógica de leitura do PDF
        try:
            reader = PdfReader(prova_path)
            texto_bruto = "\n".join(p.extract_text() or "" for p in reader.pages)
        except Exception as e:
            print(f"Erro ao ler o PDF '{prova_path}': {e}")
            texto_bruto = ""
        
        # Lógica de parsing da estrutura
        if texto_bruto:
            texto_compacto = re.sub(r"\s+", "", texto_bruto)
            questoes = []
            for n, enun, pts, corpo in HEAD_RX.findall(texto_compacto):
                q_data = {
                    "numero": int(n),
                    "pergunta": enun.strip(),
                    "pontos": float(pts),
                    "alternativas": {},
                    "tipo": "discursiva"
                }
                corpo = corpo.lstrip()
                if corpo.startswith("A"):
                    q_data["tipo"] = "multipla_escolha"
                    q_data["alternativas"] = {
                        letra: texto.strip() for letra, flag, texto in ALT_RX.findall(corpo)
                    }
                questoes.append(q_data)
            
            if questoes:
                self.dadosProva = questoes
                print(f"MODEL: {len(self.dadosProva)} questões lidas e estruturadas.")
            else:
                print(f"MODEL: ERRO - Nenhuma questão encontrada em '{prova_path}'.")
        else:
            print(f"MODEL: ERRO - Falha ao ler o arquivo da prova em '{prova_path}'.")