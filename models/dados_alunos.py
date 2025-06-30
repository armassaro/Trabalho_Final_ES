# Trabalho_Final_ES/models/dados_alunos.py
import re
import os
from PyPDF2 import PdfReader
from models.model_ia import IAModel  # Importa o modelo de IA
# ... (Regex e a classe DadosAlunos permanecem os mesmos até o método calcularNota) ...
HEADER_RX = re.compile(
    r"Nome:\s*([A-Za-zÀ-ÿ ]+?)\s*RA:\s*(\d{7})",
    re.IGNORECASE | re.DOTALL
)
HEAD_RX = re.compile(
    r"\((\d+)\)(.*?)\((\d+(?:\.\d+)?)(?:Pontos|pts?)\)(.*?)"
    r"(?=\(\d+\)|$)", re.DOTALL
)
ALT_RX = re.compile(
    r"([A-E])\(([^)]*)\)(.*?)"
    r"(?=[A-E]\(|R:|$)", re.DOTALL
)
RESP_RX = re.compile(r"R:([^A-E()]*)", re.DOTALL)


class DadosAlunos:
    def __init__(self):
        self.dadosAlunos = []

    def lerProvas(self, provas_paths: list[str]):
        # Lê as respostas dos alunos a partir de seus arquivos de prova em PDF.
        print(f"MODEL: Lendo as respostas de {len(provas_paths)} alunos...")
        self.dadosAlunos = []

        for path in provas_paths:
            print(f"MODEL: Processando '{path}'...")
            
            try:
                reader = PdfReader(path)
                texto_bruto = "\n".join(p.extract_text() or "" for p in reader.pages)
            except Exception as e:
                print(f"Erro ao ler o PDF '{path}': {e}")
                continue

            # Parse Header
            nome_aluno = "Desconhecido"
            header_match = HEADER_RX.search(texto_bruto)
            if header_match:
                nome_aluno = header_match.group(1).strip()
            else:
                nome_aluno = os.path.splitext(os.path.basename(path))[0]

            # Parse Respostas
            respostas = []
            texto_compacto = re.sub(r"\s+", "", texto_bruto)
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
            
            self.dadosAlunos.append({
                "nome": nome_aluno,
                "respostas": respostas,
                "nota": 0,
                "justificativas": [] # Armazena feedback da IA
            })
        print("MODEL: Respostas dos alunos lidas.")


    def calcularNota(self, gabarito: list, estrutura_prova: list):
        # Calcula a nota de cada aluno, usando o TIPO da questão para decidir a correção.
        print("MODEL: Iniciando cálculo de notas...")
        if not gabarito:
            print("MODEL: Aviso - Gabarito está vazio. Impossível calcular notas.")
            return
        
        ia = IAModel()

        for aluno in self.dadosAlunos:
            nota_final = 0
            aluno["justificativas"] = [""] * len(estrutura_prova)

            for i, resposta_aluno in enumerate(aluno["respostas"]):
                if i >= len(gabarito) or i >= len(estrutura_prova):
                    continue

                questao_atual = estrutura_prova[i]
                resposta_correta = gabarito[i]
                tipo_questao = questao_atual.get('tipo')

                # Decide o método de correção com base no tipo da questão
                if tipo_questao == 'discursiva':
                    pergunta = questao_atual.get('pergunta', '')
                    pontos_questao = questao_atual.get('pontos', 0)
                    
                    if not resposta_aluno or resposta_aluno == "N/A":
                        aluno['justificativas'][i] = "O aluno não forneceu uma resposta para esta questão."
                        continue

                    # IA avalia a resposta do aluno usando a resposta do gabarito como ideal
                    avaliacao = ia.avaliar_resposta_aluno(
                        pergunta=pergunta,
                        gabarito=resposta_correta, # A resposta ideal vem do gabarito gerado
                        resposta_aluno=resposta_aluno,
                        nota_maxima=pontos_questao
                    )
                    
                    nota_questao_ia = avaliacao.get('nota', 0)
                    justificativa_ia = avaliacao.get('justificativa', 'Não foi possível gerar uma justificativa.')
                    nota_atribuida = min(float(nota_questao_ia), float(pontos_questao))
                    
                    nota_final += nota_atribuida
                    aluno['justificativas'][i] = justificativa_ia

                elif tipo_questao == 'multipla_escolha':
                    # Comparação direta para múltipla escolha
                    if resposta_aluno == resposta_correta:
                        nota_final += questao_atual.get('pontos', 0)
            
            aluno['nota'] = round(nota_final, 2)
        print("\nMODEL: Notas calculadas com sucesso.")

    @staticmethod
    def validarNota(novo_valor, valor_max_str):
        if novo_valor == "":
            return True
        try:
            valor_max = float(valor_max_str)
            nota = float(novo_valor)
        except ValueError:
            return False
        return 0 <= nota <= valor_max