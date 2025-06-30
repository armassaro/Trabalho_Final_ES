import tkinter as tk
from tkinter import filedialog, scrolledtext
import os
from models.dados_alunos import DadosAlunos

class InterfacePrincipal:
    def __init__(self, root, controller):
        self.root = root
        self.controller = controller
        self.label_arquivo_prova = None
        self.label_arquivo_gabarito = None
        self.log_status_widget = None

    def limparJanela(self):
        """Remove todos os widgets da janela root."""
        for widget in self.root.winfo_children():
            widget.destroy()

    def mostraUpload(self):
        """
        Cria a tela de envio de arquivos, com conteúdo dos frames centralizado.
        """
        self.limparJanela()
        self.root.title("Envio de Arquivos")
        
        main_frame = tk.Frame(self.root, padx=10, pady=10)
        main_frame.pack(expand=True, fill=tk.BOTH)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)

        # --- Área de Upload de Provas (Esquerda) ---
        provas_frame = tk.LabelFrame(main_frame, text=" Solte e arraste os documentos contendo as provas aqui ", padx=20, pady=20, font=("Arial", 10))
        provas_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        provas_frame.grid_propagate(False)
        
        provas_content_frame = tk.Frame(provas_frame)
        provas_content_frame.pack(expand=True)

        tk.Label(provas_content_frame, text="(formatos suportados: .pdf)", fg="gray").pack(pady=(0, 20))
        tk.Label(provas_content_frame, text="...ou clique abaixo para escolher o arquivo").pack(pady=10)
        tk.Button(provas_content_frame, text="Escolher arquivos", command=self.selecionarArquivos).pack(pady=10)
        self.label_arquivo_prova = tk.Label(provas_content_frame, text="Nenhum arquivo selecionado", font=("Arial", 9), fg="gray", wraplength=300)
        self.label_arquivo_prova.pack(pady=10)

        # --- Área de Upload de Gabarito (Direita) ---
        gabarito_frame = tk.LabelFrame(main_frame, text=" Solte e arraste os documentos contendo o gabarito aqui ", padx=20, pady=20, font=("Arial", 10))
        gabarito_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        gabarito_frame.grid_propagate(False)

        gabarito_content_frame = tk.Frame(gabarito_frame)
        gabarito_content_frame.pack(expand=True)

        tk.Label(gabarito_content_frame, text="(não obrigatório)", fg="red").pack()
        tk.Label(gabarito_content_frame, text="(formatos suportados: .pdf)", fg="gray").pack(pady=(0, 20))
        tk.Label(gabarito_content_frame, text="...ou clique abaixo para escolher o arquivo").pack(pady=10)
        tk.Button(gabarito_content_frame, text="Escolher arquivo", command=self.selecionarGabarito).pack(pady=10)
        self.label_arquivo_gabarito = tk.Label(gabarito_content_frame, text="Nenhum arquivo selecionado", font=("Arial", 9), fg="gray", wraplength=300)
        self.label_arquivo_gabarito.pack(pady=10)

        # --- Botões Inferiores ---
        bottom_frame = tk.Frame(self.root, pady=10, padx=20)
        bottom_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        btn_ajuda = tk.Button(bottom_frame, text="Ajuda", command=lambda: self.controller.chamaJanela("ajuda"))
        btn_ajuda.pack(side=tk.RIGHT)
        
        btn_enviar = tk.Button(bottom_frame, text="Enviar", command=lambda: self.controller.chamaJanela("status"))
        btn_enviar.pack(side=tk.RIGHT, padx=10)

    def mostraAjuda(self):
        """Cria a tela de Ajuda, conforme o protótipo."""
        self.limparJanela()
        self.root.title("Ajuda")

        tk.Label(self.root, text="Ajuda do Sistema", font=("Arial", 16, "bold"), pady=10).pack()
        
        texto_ajuda = """
        Este sistema realiza a correção automatizada de provas para otimizar o tempo de professores.

        1. Envio de Arquivos: Na tela principal, clique em "Escolher arquivos" para selecionar uma ou mais provas de alunos em formato PDF.
        
        2. Gabarito (Opcional): Você pode enviar um arquivo de gabarito para questões objetivas. Se não for enviado, a IA irá gerar as respostas.

        3. Processamento: Após clicar em "Enviar", o sistema irá extrair os textos, comparar as respostas e atribuir as notas.

        4. Resultados: Na tela de resultados, você pode visualizar a comparação entre a resposta do aluno e a resposta da IA, além de poder ajustar a nota final.
        """
        
        tk.Message(self.root, text=texto_ajuda, width=550, justify=tk.LEFT, font=("Arial", 10)).pack(pady=10, padx=20)
        tk.Button(self.root, text="Voltar", command=lambda: self.controller.chamaJanela("upload")).pack(pady=20)

    def mostraStatus(self):
        """Cria a tela de Carregamento/Status, conforme o protótipo."""
        self.limparJanela()
        self.root.title("Processando...")

        tk.Label(self.root, text="Processando Arquivos", font=("Arial", 16, "bold"), pady=10).pack()
        
        self.log_status_widget = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, height=15, width=70, font=("Courier New", 9))
        self.log_status_widget.pack(pady=10, padx=10)
        self.log_status_widget.config(state=tk.DISABLED)

        tk.Button(self.root, text="Cancelar", command=self.root.quit).pack(pady=10)

    def adicionarLogStatus(self, mensagem: str):
        """Adiciona uma nova linha de log na tela de status."""
        if self.log_status_widget:
            self.log_status_widget.config(state=tk.NORMAL)
            self.log_status_widget.insert(tk.END, mensagem + "\n")
            self.log_status_widget.see(tk.END)
            self.log_status_widget.config(state=tk.DISABLED)

    def mostraResultados(self, dados_alunos: list, dados_prova: list):
        """Cria a tela de Comparação de Respostas, usando os dados processados."""
        self.limparJanela()
        self.root.title("Resultados da Correção")

        if not dados_alunos or not dados_prova:
            tk.Label(self.root, text="Não há dados suficientes para exibir os resultados.", font=("Arial", 16)).pack(pady=50)
            tk.Button(self.root, text="Voltar", command=lambda: self.controller.chamaJanela("upload")).pack()
            return

        aluno_atual = dados_alunos[0]
        questao_atual = dados_prova[0]
        
        top_frame = tk.Frame(self.root, padx=10, pady=10)
        top_frame.pack(fill=tk.X)
        
        content_frame = tk.Frame(self.root, padx=10)
        content_frame.pack(expand=True, fill=tk.BOTH)
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_columnconfigure(1, weight=1)

        bottom_frame = tk.Frame(self.root, padx=10, pady=10)
        bottom_frame.pack(fill=tk.X)

        tk.Label(top_frame, text=f"Nome do aluno: {aluno_atual.get('nome', 'N/A')}", font=("Arial", 12)).pack(side=tk.LEFT)
        tk.Button(top_frame, text="Próximo >").pack(side=tk.RIGHT)
        tk.Label(top_frame, text=f"Questão nº: 1", font=("Arial", 12)).pack(side=tk.RIGHT, padx=5)
        tk.Button(top_frame, text="< Anterior").pack(side=tk.RIGHT)

        enunciado = questao_atual.get('questao', '')
        tk.Label(content_frame, text="Enunciado da Questão:", font=("Arial", 10, "bold")).grid(row=0, column=0, columnspan=2, sticky="w", pady=(5,0))
        enunciado_text = tk.Text(content_frame, height=5, wrap=tk.WORD, relief=tk.FLAT, background=self.root.cget('bg'), state="disabled")
        enunciado_text.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        enunciado_text.config(state="normal")
        enunciado_text.insert(tk.END, enunciado)
        enunciado_text.config(state="disabled")

        tk.Label(content_frame, text="Resposta do Aluno:", font=("Arial", 10, "bold")).grid(row=2, column=0, sticky="w")
        resp_aluno_text = tk.Text(content_frame, height=10, wrap=tk.WORD, relief=tk.SOLID, borderwidth=1)
        resp_aluno_text.grid(row=3, column=0, sticky="nsew", padx=(0, 5))
        resp_aluno_text.insert(tk.END, aluno_atual.get('respostas', ['N/A'])[0])
        resp_aluno_text.config(state="disabled")

        tk.Label(content_frame, text="Resposta do Gabarito:", font=("Arial", 10, "bold")).grid(row=2, column=1, sticky="w")
        resp_ia_text = tk.Text(content_frame, height=10, wrap=tk.WORD, relief=tk.SOLID, borderwidth=1)
        resp_ia_text.grid(row=3, column=1, sticky="nsew", padx=(5, 0))
        if self.controller.dados_gabarito.dadosGabarito:
            resp_ia_text.insert(tk.END, self.controller.dados_gabarito.dadosGabarito[0])
        resp_ia_text.config(state="disabled")

        nota_frame = tk.Frame(content_frame)
        nota_frame.grid(row=4, column=0, columnspan=2, sticky="w", pady=10)
        
        valor_q = questao_atual.get('valorQuestao', 0)
        
        tk.Label(nota_frame, text=f"Valor da questão: {valor_q} pts").pack(side=tk.LEFT, padx=5)
        tk.Label(nota_frame, text=f"Nota Total do Aluno: {aluno_atual.get('nota', 0)} pts").pack(side=tk.LEFT, padx=5)
        
        vcmd = (self.root.register(DadosAlunos.validarNota), '%P', str(valor_q))
        
        tk.Label(nota_frame, text="Ajustar nota da questão:", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=(20, 0))
        
        nota_entry = tk.Entry(nota_frame, width=5, validate='key', validatecommand=vcmd)
        nota_entry.pack(side=tk.LEFT, padx=5)

        tk.Button(bottom_frame, text="Exportar Planilha").pack(side=tk.RIGHT)

    def selecionarArquivos(self):
        """Abre o diálogo para selecionar múltiplos arquivos de prova."""
        paths = filedialog.askopenfilenames(title="Selecionar provas", filetypes=[("PDF", "*.pdf")])
        if paths:
            self.controller.setCaminhosProvas(paths)
            if len(paths) == 1:
                nome_display = os.path.basename(paths[0])
            else:
                nome_display = f"{len(paths)} arquivos selecionados"
            self.label_arquivo_prova.config(text=nome_display, fg="blue")

    def selecionarGabarito(self):
        """Abre o diálogo para selecionar um único arquivo de gabarito."""
        path = filedialog.askopenfilename(title="Selecionar gabarito", filetypes=[("PDF", "*.pdf"), ("Text", "*.txt")])
        if path:
            self.controller.setCaminhoGabarito(path)
            self.label_arquivo_gabarito.config(text=os.path.basename(path), fg="blue")