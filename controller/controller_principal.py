import tkinter as tk
from tkinter import messagebox
from view.interface_principal import InterfacePrincipal
from models.dados_alunos import DadosAlunos
from models.dados_gabarito import DadosGabarito
from models.dados_prova import DadosProva
from PyPDF2 import PdfReader
import time
import os

class ControllerPrincipal:
    def __init__(self):
        self.root = tk.Tk()
        self.interface = InterfacePrincipal(self.root, self)
        
        # Atributos definidos no diagrama UML
        self.estadoApp = "inicial"
        self.statusCorrecao = "pendente"
        
        # Atributos para armazenar os caminhos dos arquivos
        self.caminhos_provas = []
        self.caminho_gabarito = ""

        # Instanciação dos modelos, conforme o diagrama
        self.dados_alunos = DadosAlunos()
        self.dados_gabarito = DadosGabarito()
        self.dados_prova = DadosProva()

    def _centralizar_janela(self, largura, altura):
        """Calcula a posição para centralizar a janela principal na tela."""
        largura_tela = self.root.winfo_screenwidth()
        altura_tela = self.root.winfo_screenheight()
        pos_x = (largura_tela // 2) - (largura // 2)
        pos_y = (altura_tela // 2) - (altura // 2)
        self.root.geometry(f'{largura}x{altura}+{pos_x}+{pos_y}')
        self.root.resizable(False, False)

    def iniciar(self):
        """Inicia a aplicação exibindo a primeira janela."""
        self.estadoApp = "rodando"
        self.chamaJanela("upload")
        self.root.mainloop()

    def chamaJanela(self, janela: str):
        # Gerencia a transição entre as diferentes telas da aplicação.
        if janela == "upload":
            self._centralizar_janela(800, 450)
            self.interface.mostraUpload() #
        elif janela == "ajuda":
            self._centralizar_janela(600, 400)
            self.interface.mostraAjuda() #
        elif janela == "status":
            if not self.caminhos_provas:
                messagebox.showwarning("Nenhuma Prova", "Por favor, selecione ao menos um arquivo de prova antes de enviar.")
                return
            self._centralizar_janela(600, 400)
            self.iniciar_processamento()
        elif janela == "resultados":
            self._centralizar_janela(900, 650)
            # Passa os dados reais processados para a tela de resultados
            self.interface.mostraResultados(self.dados_alunos.dadosAlunos, self.dados_prova.dadosProva) #

    def iniciar_processamento(self):
        """Orquestra o processo de correção chamando os modelos, conforme o diagrama."""
        self.interface.mostraStatus() #
        self.statusCorrecao = "processando"
        self.interface.adicionar_log_status(f"Status da Correção: {self.statusCorrecao}")
        
        def processar():
            try:
                # ITEM 5: Ler a estrutura da prova (usando o primeiro arquivo como base)
                self.interface.adicionar_log_status("Lendo estrutura da prova...")
                leitor_base = PdfReader(self.caminhos_provas[0])
                self.dados_prova.lerProva(leitor_base) #
                self.root.update_idletasks()
                
                # ITEM 6: Processar Gabarito (se houver)
                if self.caminho_gabarito:
                    nome_gabarito = os.path.basename(self.caminho_gabarito)
                    self.interface.adicionar_log_status(f"Lendo gabarito de: {nome_gabarito}...")
                    gabarito_reader = PdfReader(self.caminho_gabarito)
                    self.dados_gabarito.lerGabarito(gabarito_reader) #
                    self.root.update_idletasks()

                # ITEM 4: Ler as provas dos alunos
                self.interface.adicionar_log_status(f"Lendo as respostas de {len(self.caminhos_provas)} aluno(s)...")
                leitores_provas = [PdfReader(path) for path in self.caminhos_provas]
                self.dados_alunos.lerProvas(leitores_provas, self.caminhos_provas) #
                self.root.update_idletasks()

                # ITEM 4 (continuação): Calcular as notas
                self.interface.adicionar_log_status("Corrigindo provas e calculando notas...")
                self.dados_alunos.calcularNota(self.dados_gabarito.dadosGabarito, self.dados_prova.dadosProva) #
                self.root.update_idletasks()

                # ITEM 7 e 8: Finalização e chamada da tela de resultados
                self.statusCorrecao = "concluido"
                self.interface.adicionar_log_status(f"Status da Correção: {self.statusCorrecao}")
                self.root.after(1000, lambda: self.chamaJanela("resultados"))

            except Exception as e:
                self.statusCorrecao = "erro"
                self.interface.adicionar_log_status(f"\nERRO: {e}")
                messagebox.showerror("Erro no Processamento", f"Ocorreu um erro: {e}")

        # Roda o processamento após a janela de status ser exibida
        self.root.after(100, processar)

    def set_caminhos_provas(self, paths):
        self.caminhos_provas = paths

    def set_caminho_gabarito(self, path):
        self.caminho_gabarito = path