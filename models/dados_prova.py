from PyPDF2 import PdfReader

class DadosProva:
    def __init__(self):
        self.dadosProva = []

    def lerProva(self, prova: PdfReader):
        """
        Simula a leitura da estrutura da prova (questões, valores, etc.).
        Este método preenche a lista self.dadosProva com os detalhes de cada questão.
        """
        print("MODEL: Lendo a estrutura da prova...")
        # Limpa dados anteriores
        self.dadosProva = [] 
        
        # Simulação: Extrai dados de um PDF de prova "template"
        # Na prática, isso envolveria uma lógica complexa de extração de texto.
        self.dadosProva.append({
            "questao": "1. Qual dos jogos abaixo é considerado o primeiro videogame comercial da história?",
            "valorQuestao": 0.5,
            "conteudoQuestao": "História dos Games",
            "alternativas": ["A) Pong", "B) Space Invaders", "C) Tennis for Two", "D) Magnavox Odyssey"]
        })
        self.dadosProva.append({
            "questao": "2. Em The Legend of Zelda, quem é o protagonista da série?",
            "valorQuestao": 0.5,
            "conteudoQuestao": "Personagens",
            "alternativas": ["A) Zelda", "B) Ganon", "C) Link", "D) Hyrule"]
        })
        # Adicione mais questões conforme necessário para a simulação
        print(f"MODEL: {len(self.dadosProva)} questões lidas e estruturadas.")