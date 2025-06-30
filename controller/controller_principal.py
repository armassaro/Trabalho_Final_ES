# Trabalho_Final_ES/controller/controller_principal.py
import tkinter as tk
from tkinter import messagebox
from view.interface_principal import InterfacePrincipal
from models.dados_alunos import DadosAlunos
from models.dados_gabarito import DadosGabarito
from models.dados_prova import DadosProva
from controller.controller_ia import controller_ia as ControllerIA # Importa a classe da IA
import time
import os

class ControllerPrincipal:
    # ... (init, centralizarJanela, iniciar, chamaJanela - sem alterações) ...
    def __init__(self):
        self.root = tk.Tk()
        self.interface = InterfacePrincipal(self.root, self)
        self.estadoApp = "inicial"
        self.statusCorrecao = "pendente"
        self.caminhos_provas = []
        self.caminho_gabarito = ""
        self.dados_alunos = DadosAlunos()
        self.dados_gabarito = DadosGabarito()
        self.dados_prova = DadosProva()
        self.aluno_atual_idx = 0
        self.questao_atual_idx = 0

    def centralizarJanela(self, largura, altura):
        largura_tela = self.root.winfo_screenwidth()
        altura_tela = self.root.winfo_screenheight()
        pos_x = (largura_tela // 2) - (largura // 2)
        pos_y = (altura_tela // 2) - (altura // 2)
        self.root.geometry(f'{largura}x{altura}+{pos_x}+{pos_y}')
        self.root.resizable(False, False)

    def iniciar(self):
        self.estadoApp = "rodando"
        self.chamaJanela("upload")
        self.root.mainloop()

    def chamaJanela(self, janela: str):
        if janela == "upload":
            self.centralizarJanela(800, 450)
            self.interface.mostraUpload()
        elif janela == "ajuda":
            self.centralizarJanela(600, 400)
            self.interface.mostraAjuda()
        elif janela == "status":
            if not self.caminhos_provas:
                messagebox.showwarning("Nenhuma Prova", "Por favor, selecione ao menos um arquivo de prova antes de enviar.")
                return
            self.centralizarJanela(600, 400)
            self.iniciarProcessamento()
        elif janela == "resultados":
            self.centralizarJanela(900, 650)
            self.aluno_atual_idx = 0
            self.questao_atual_idx = 0
            self.interface.mostraResultados()


    def iniciarProcessamento(self):
        # Orquestra todo o processo de correção.
        self.interface.mostraStatus()
        self.statusCorrecao = "processando"
        self.interface.adicionarLogStatus(f"Status da Correção: {self.statusCorrecao}")
        
        def processar():
            try:
                # 1. Ler a estrutura da prova a partir do primeiro arquivo
                self.interface.adicionarLogStatus("Lendo estrutura da prova...")
                self.dados_prova.lerProva(self.caminhos_provas[0])
                self.root.update_idletasks()
                
                # 2. Verificar se o gabarito foi fornecido. Se não, gerar com a IA.
                if self.caminho_gabarito:
                    self.interface.adicionarLogStatus("Lendo gabarito fornecido...")
                    self.dados_gabarito.lerGabarito(self.caminho_gabarito)
                else:
                    self.interface.adicionarLogStatus("Gabarito não fornecido. Gerando com IA...")
                    self.root.update_idletasks()
                    ia = ControllerIA()
                    respostas_gabarito_ia = []
                    for questao in self.dados_prova.dadosProva:
                        pergunta = questao.get('pergunta', '')
                        # Adiciona as alternativas na pergunta para dar contexto à IA
                        if questao.get('tipo') == 'multipla_escolha':
                            alternativas_texto = "\n".join([f"{key}) {val}" for key, val in questao['alternativas'].items()])
                            pergunta_completa = f"{pergunta}\n{alternativas_texto}"
                        else:
                            pergunta_completa = pergunta
                        
                        resposta = ia.gerarRespostaGabarito(pergunta_completa)
                        respostas_gabarito_ia.append(resposta)
                        self.interface.adicionarLogStatus(f"-> Resposta da IA para Questão {questao['numero']}: {resposta}")
                        self.root.update_idletasks()
                    
                    self.dados_gabarito.dadosGabarito = respostas_gabarito_ia

                # 3. Ler as provas dos alunos
                self.interface.adicionarLogStatus("Lendo as respostas dos alunos...")
                self.dados_alunos.lerProvas(self.caminhos_provas)
                self.root.update_idletasks()

                # 4. Calcular as notas (aqui a IA pode ser chamada novamente para correção)
                self.interface.adicionarLogStatus("Corrigindo provas e calculando notas...")
                self.dados_alunos.calcularNota(self.dados_gabarito.dadosGabarito, self.dados_prova.dadosProva)
                self.root.update_idletasks()

                # 5. Finalização
                self.statusCorrecao = "concluido"
                self.interface.adicionarLogStatus(f"\nStatus da Correção: {self.statusCorrecao}")
                self.root.after(1000, lambda: self.chamaJanela("resultados"))

            except Exception as e:
                self.statusCorrecao = "erro"
                self.interface.adicionarLogStatus(f"\nERRO INESPERADO: {e}")
                messagebox.showerror("Erro no Processamento", f"Ocorreu um erro: {e}")

        self.root.after(100, processar)
    
    # ... (mudar_aluno, mudar_questao, get_dados_para_resultados, setCaminhos - sem alterações) ...
    def mudar_aluno(self, delta: int):
        num_alunos = len(self.dados_alunos.dadosAlunos)
        if num_alunos > 0:
            self.aluno_atual_idx = (self.aluno_atual_idx + delta) % num_alunos
            self.questao_atual_idx = 0
            self.interface.atualizar_resultados()

    def mudar_questao(self, delta: int):
        num_questoes = len(self.dados_prova.dadosProva)
        if num_questoes > 0:
            self.questao_atual_idx = (self.questao_atual_idx + delta) % num_questoes
            self.interface.atualizar_resultados()

    def get_dados_para_resultados(self):
        if not self.dados_alunos.dadosAlunos or not self.dados_prova.dadosProva:
            return None

        aluno_atual = self.dados_alunos.dadosAlunos[self.aluno_atual_idx]
        questao_atual = self.dados_prova.dadosProva[self.questao_atual_idx]

        resposta_aluno = "Sem resposta"
        if 'respostas' in aluno_atual and self.questao_atual_idx < len(aluno_atual['respostas']):
            resposta_aluno = aluno_atual['respostas'][self.questao_atual_idx]

        resposta_gabarito = "Gabarito não fornecido"
        if self.dados_gabarito.dadosGabarito and self.questao_atual_idx < len(self.dados_gabarito.dadosGabarito):
            resposta_gabarito = self.dados_gabarito.dadosGabarito[self.questao_atual_idx]
        
        return {
            "aluno": aluno_atual,
            "questao": questao_atual,
            "resposta_aluno": resposta_aluno,
            "resposta_gabarito": resposta_gabarito,
            "aluno_idx": self.aluno_atual_idx,
            "total_alunos": len(self.dados_alunos.dadosAlunos),
            "questao_idx": self.questao_atual_idx,
            "total_questoes": len(self.dados_prova.dadosProva)
        }

    def setCaminhosProvas(self, paths):
        self.caminhos_provas = paths

    def setCaminhoGabarito(self, path):
        self.caminho_gabarito = path