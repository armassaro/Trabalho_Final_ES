# A importação do PdfReader não é mais necessária aqui.
# from PyPDF2 import PdfReader

class DadosGabarito:
    def __init__(self):
        self.dadosGabarito = []

    def lerGabarito(self, caminho_gabarito: str):
        """
        Lê um arquivo de gabarito em formato de texto (.txt) e extrai as respostas.
        Formato esperado no arquivo: "1. A", "2. C", etc.
        """
        print(f"MODEL: Lendo o gabarito de '{caminho_gabarito}'...")
        self.dadosGabarito = []
        try:
            with open(caminho_gabarito, 'r', encoding='utf-8') as f:
                for linha in f:
                    if '.' in linha:
                        # Pega a parte depois do primeiro ponto e remove espaços
                        resposta = linha.split('.', 1)[1].strip()
                        self.dadosGabarito.append(resposta)
            print(f"MODEL: Gabarito lido com {len(self.dadosGabarito)} respostas.")
        except FileNotFoundError:
            print(f"MODEL: ERRO - Arquivo de gabarito não encontrado em '{caminho_gabarito}'")
        except Exception as e:
            print(f"MODEL: ERRO ao ler gabarito: {e}")