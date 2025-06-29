from PyPDF2 import PdfReader
import os

class DadosAlunos:
    def __init__(self):
        # Alterado para lista, conforme especificado no fluxograma
        self.dadosAlunos = []

    def lerProvas(self, provas: list[PdfReader], nomes_arquivos: list[str]):
        """
        Simula a leitura das respostas dos alunos a partir de seus arquivos de prova.
        Preenche a lista self.dadosAlunos com nome e respostas.
        """
        print(f"MODEL: Lendo as respostas de {len(provas)} alunos...")
        self.dadosAlunos = [] # Limpa dados anteriores

        for i, prova_reader in enumerate(provas):
            # Simulação: Extrai nome do aluno do nome do arquivo
            nome_aluno = os.path.splitext(os.path.basename(nomes_arquivos[i]))[0]
            
            # Simulação: Extrai as respostas do aluno do PDF
            respostas_aluno = ["D", "A"] # Simula que o aluno 1 acertou a primeira e errou a segunda
            if i % 2 != 0:
                 respostas_aluno = ["B", "B"] # Simula respostas diferentes para outros alunos

            self.dadosAlunos.append({
                "nome": nome_aluno,
                "respostas": respostas_aluno,
                "nota": 0 # Nota inicial
            })
        print("MODEL: Respostas dos alunos lidas.")


    def calcularNota(self, gabarito: list, estrutura_prova: list):
        """
        Simula o cálculo da nota de cada aluno, comparando suas respostas
        com o gabarito e usando o valor de cada questão da estrutura da prova.
        """
        print("MODEL: Calculando notas...")
        if not gabarito:
            print("MODEL: Aviso - Não há gabarito para calcular as notas.")
            return

        for aluno in self.dadosAlunos:
            nota_final = 0
            for i, resposta_aluno in enumerate(aluno["respostas"]):
                if i < len(gabarito) and resposta_aluno == gabarito[i]:
                    # Adiciona o valor da questão se a resposta estiver correta
                    nota_final += estrutura_prova[i]['valorQuestao']
            aluno['nota'] = round(nota_final, 2)
        print("MODEL: Notas calculadas.")


    def validar_nota(novo_valor, valor_max_str):
        if novo_valor == "":
            return True
        try:
            valor_max = float(valor_max_str)
            nota = float(novo_valor)
        except ValueError:
            return False
        return 0 <= nota <= valor_max