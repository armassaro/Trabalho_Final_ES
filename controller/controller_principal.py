# Trabalho_Final_ES/controller/controller_principal.py
import tkinter as tk
from tkinter import messagebox, filedialog
from view.interface_principal import InterfacePrincipal
from models.dados_alunos import DadosAlunos
from models.dados_gabarito import DadosGabarito
from models.dados_prova import DadosProva
from .controller_ia import ControllerIA
from csv_export import csv_export as CsvExport
import time
import os
import traceback

class ControllerPrincipal:
    def __init__(self):
        self.root = tk.Tk()
        self.interface = InterfacePrincipal(self.root, self)
        self.estadoApp = "inicial"
        self.statusCorrecao = "pendente"
        self.caminhos_provas = []
        self.caminho_gabarito = ""
        self.controller_ia = ControllerIA()
        self.dados_alunos = DadosAlunos()
        self.dados_gabarito = DadosGabarito()
        self.dados_prova = DadosProva()
        self.aluno_atual_idx = 0
        self.questao_atual_idx = 0
        # Variável interna para ativar o modo de depuração
        self.debug_mode = True

    def centralizarJanela(self, largura, altura):
        """Centraliza a janela na tela"""
        largura_tela = self.root.winfo_screenwidth()
        altura_tela = self.root.winfo_screenheight()
        pos_x = (largura_tela // 2) - (largura // 2)
        pos_y = (altura_tela // 2) - (altura // 2)
        self.root.geometry(f'{largura}x{altura}+{pos_x}+{pos_y}')
        self.root.resizable(False, False)

    def iniciar(self):
        """Inicia a aplicação"""
        self.estadoApp = "rodando"
        self.chamaJanela("upload")
        self.root.mainloop()

    def chamaJanela(self, janela: str):
        """Gerencia a transição entre janelas"""
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

    def normalizar_questoes(self):
        """Normaliza as questões para os tipos suportados pelo IAModel"""
        for questao in self.dados_prova.dadosProva:
            if questao.get('tipo') in ['multipla_escolha', 'objetiva']:
                questao['tipo'] = 'objetiva'
            else:
                questao['tipo'] = 'dissertativa'

    def iniciarProcessamento(self):
        """Orquestra todo o processo de correção, com modo de debug"""
        self.interface.mostraStatus()
        self.statusCorrecao = "processando"
        self.interface.adicionarLogStatus(f"Status da Correção: {self.statusCorrecao}")
        
        def processar():
            try:
                # Etapas comuns a ambos os modos
                self.interface.adicionarLogStatus("Lendo estrutura da prova...")
                self.dados_prova.lerProva(self.caminhos_provas[0])
                self.normalizar_questoes()
                self.root.update_idletasks()

                self.interface.adicionarLogStatus("Lendo respostas dos alunos...")
                self.dados_alunos = DadosAlunos(debug=self.debug_mode)
                self.dados_alunos.lerProvas(self.caminhos_provas)
                self.root.update_idletasks()

                if self.debug_mode:
                    # Lógica do modo de depuração: pula IA
                    self.interface.adicionarLogStatus("\n*** MODO DEBUG ATIVADO ***")
                    self.interface.adicionarLogStatus("Pulando processamento com IA.")
                    
                    # Cria uma estrutura de dados compatível sem notas da IA
                    resultados_debug = []
                    for aluno in self.dados_alunos.dadosAlunos:
                        aluno_data = {
                            **aluno,
                            'nota': 0.0, # Nota padrão
                            'nota_total': 0.0,
                            'questoes': [{'numero': q['numero'], 'nota': 0, 'feedback': 'Modo Debug'} for q in self.dados_prova.dadosProva]
                        }
                        resultados_debug.append(aluno_data)
                    self.dados_alunos.dadosAlunos = resultados_debug
                    self.interface.adicionarLogStatus("Dados de debug gerados.")
                else:
                    # Processamento completo com IA
                    if self.caminho_gabarito:
                        self.interface.adicionarLogStatus("Lendo gabarito fornecido...")
                        self.dados_gabarito.lerGabarito(self.caminho_gabarito)
                    else:
                        self.interface.adicionarLogStatus("Gerando gabarito com IA...")
                        gabarito_ia = self.controller_ia.gerar_gabarito(self.dados_prova.dadosProva)
                        self.dados_gabarito.dadosGabarito = gabarito_ia
                        for i, resp in enumerate(gabarito_ia, 1):
                            self.interface.adicionarLogStatus(f"Questão {i}: {resp}")
                        self.root.update_idletasks()

                    self.interface.adicionarLogStatus("Corrigindo provas...")
                    resultados = []
                    for aluno in self.dados_alunos.dadosAlunos:
                        resultado = self.controller_ia.corrigir_prova(
                            aluno,
                            self.dados_prova.dadosProva,
                            self.dados_gabarito.dadosGabarito
                        )
                        # Garante compatibilidade da chave 'nota'
                        resultado['nota'] = resultado.get('nota_total', 0)
                        resultados.append(resultado)
                        self.interface.adicionarLogStatus(f"Corrigido: {aluno['nome']} - Nota: {resultado['nota']}")
                        self.root.update_idletasks()
                    
                    self.dados_alunos.dadosAlunos = resultados

                self.statusCorrecao = "concluido"
                self.interface.adicionarLogStatus(f"\nStatus da Correção: {self.statusCorrecao}")
                self.root.after(1000, lambda: self.chamaJanela("resultados"))

            except Exception as e:
                self.statusCorrecao = "erro"
                self.interface.adicionarLogStatus(f"\nERRO: {str(e)}")
                messagebox.showerror("Erro", f"Ocorreu um erro durante o processamento:\n{str(e)}")
                self.interface.adicionarLogStatus(f"Detalhes do erro:\n{traceback.format_exc()}")

        self.root.after(100, processar)

    def exportar_para_csv(self):
        """Pega os dados em memória e exporta para um arquivo CSV."""
        if not self.dados_alunos.dadosAlunos:
            messagebox.showwarning("Sem Dados", "Não há dados de alunos para exportar.")
            return

        try:
            exporter = CsvExport()
            
            # Constrói o conteúdo do CSV
            exporter.adicionaHeader()
            exporter.adicionaNotasEstudantes(self.dados_alunos.dadosAlunos)
            
            csv_content = exporter.getConteudoCsv()
            
            # Salva o arquivo no diretório atual
            file_path = "relatorio_desempenho.csv"
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                f.write(csv_content)
                
            messagebox.showinfo("Sucesso", f"Relatório exportado com sucesso para:\n{os.path.abspath(file_path)}")

        except Exception as e:
            messagebox.showerror("Erro de Exportação", f"Ocorreu um erro ao exportar o CSV:\n{str(e)}")

    def mudar_aluno(self, delta: int):
        """Muda o aluno atual sendo visualizado"""
        num_alunos = len(self.dados_alunos.dadosAlunos)
        if num_alunos > 0:
            self.aluno_atual_idx = (self.aluno_atual_idx + delta) % num_alunos
            self.questao_atual_idx = 0
            self.interface.atualizar_resultados()

    def mudar_questao(self, delta: int):
        """Muda a questão atual sendo visualizada"""
        num_questoes = len(self.dados_prova.dadosProva)
        if num_questoes > 0:
            self.questao_atual_idx = (self.questao_atual_idx + delta) % num_questoes
            self.interface.atualizar_resultados()

    def get_dados_para_resultados(self):
        """Obtém os dados para exibição na tela de resultados"""
        if not self.dados_alunos.dadosAlunos or not self.dados_prova.dadosProva:
            return None

        aluno_atual = self.dados_alunos.dadosAlunos[self.aluno_atual_idx]
        questao_atual = self.dados_prova.dadosProva[self.questao_atual_idx]
        
        resposta_aluno = "Sem resposta"
        if self.questao_atual_idx < len(aluno_atual.get('respostas', [])):
             resposta_aluno = aluno_atual['respostas'][self.questao_atual_idx]
             if not resposta_aluno or resposta_aluno == "N/A":
                resposta_aluno = "Sem resposta"

        resposta_gabarito = "Gabarito não fornecido"
        if self.dados_gabarito.dadosGabarito and self.questao_atual_idx < len(self.dados_gabarito.dadosGabarito):
            resposta_gabarito = self.dados_gabarito.dadosGabarito[self.questao_atual_idx]
        
        feedback = ""
        nota_questao = 0
        if 'questoes' in aluno_atual and self.questao_atual_idx < len(aluno_atual['questoes']):
            feedback = aluno_atual['questoes'][self.questao_atual_idx].get('feedback', '')
            nota_questao = aluno_atual['questoes'][self.questao_atual_idx].get('nota', 0)
        
        return {
            "aluno": aluno_atual,
            "questao": questao_atual,
            "resposta_aluno": resposta_aluno,
            "resposta_gabarito": resposta_gabarito,
            "feedback": feedback,
            "nota_questao": nota_questao,
            "aluno_idx": self.aluno_atual_idx,
            "total_alunos": len(self.dados_alunos.dadosAlunos),
            "questao_idx": self.questao_atual_idx,
            "total_questoes": len(self.dados_prova.dadosProva)
        }

    def setCaminhosProvas(self, paths):
        """Define os caminhos dos arquivos de prova"""
        self.caminhos_provas = paths

    def setCaminhoGabarito(self, path):
        """Define o caminho do arquivo de gabarito"""
        self.caminho_gabarito = path