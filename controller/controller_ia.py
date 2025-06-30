# Trabalho_Final_ES/controller/controller_ia.py
import ollama
import json

class controller_ia:
    def __init__(self, model: str = "phi3:mini", temperature: float = 0.1, num_ctx: int = 2048):
        self.model = model
        self.temperature = temperature
        self.num_ctx = num_ctx

    def gerarRespostaGabarito(self, pergunta: str) -> str:
        # Gera uma resposta breve e direta para uma pergunta, ideal para um gabarito.
        print(f"🧠 IA: Gerando resposta para o gabarito da pergunta: '{pergunta[:40]}...'")

        # Prompt do sistema para gerar respostas de gabarito
        prompt_sistema = """
        Você é um assistente especialista em criar gabaritos.
        Sua tarefa é fornecer uma resposta correta, breve e direta para a pergunta enviada.
        - Se for uma questão de múltipla escolha, retorne APENAS a letra da alternativa correta (ex: A).
        - Se for uma questão discursiva, forneça uma resposta ideal e concisa.
        Não inclua frases como "A resposta é". Seja direto.
        """
        try:
            # CORREÇÃO: 'temperature' movido para dentro de 'options'
            response = ollama.chat(
                model=self.model,
                options={
                    'num_ctx': self.num_ctx,
                    'temperature': self.temperature
                },
                messages=[
                    {'role': 'system', 'content': prompt_sistema},
                    {'role': 'user', 'content': pergunta}
                ]
            )
            return response['message']['content'].strip()
        except Exception as e:
            print(f"❌ Ocorreu um erro ao chamar a API do Ollama: {e}")
            return "Erro ao gerar resposta."

    def avaliar_resposta_aluno(self, pergunta: str, gabarito: str, resposta_aluno: str, nota_maxima: int = 10) -> dict:
        # Avalia a resposta de um aluno, comparando-a com o gabarito oficial e atribuindo uma nota.
        prompt_sistema = f"""
        Você é um assistente de avaliação rigoroso, justo e objetivo.
        Sua tarefa é analisar a resposta de um aluno, compará-la com o gabarito oficial e atribuir uma nota de 0 a {nota_maxima}.
        Siga estas etapas:
        1. Entenda a 'Pergunta Original'.
        2. Estude o 'Gabarito (Resposta Ideal)'.
        3. Analise a 'Resposta do Aluno'.
        4. Compare a 'Resposta do Aluno' com o 'Gabarito'.
        5. Atribua uma nota numérica que reflita o quão próxima a resposta do aluno está do gabarito.
        6. Escreva uma 'justificativa' clara e construtiva.
        7. Retorne sua avaliação estritamente no formato JSON, com as chaves "nota" (um número) e "justificativa" (um texto).

        Exemplo de saída:
        {{
          "nota": 8.5,
          "justificativa": "O aluno demonstrou um bom entendimento sobre o ciclo da água. No entanto, não mencionou a condensação. A nota reflete a cobertura parcial dos tópicos."
        }}
        """

        prompt_usuario = f"""
        ---
        **Pergunta Original:**
        {pergunta}
        ---
        **Gabarito (Resposta Ideal):**
        {gabarito}
        ---
        **Resposta do Aluno para Avaliar:**
        {resposta_aluno}
        ---
        """

        print(f"🧠 IA: Avaliando resposta para a pergunta: '{pergunta[:40]}...'")
        try:
            # CORREÇÃO: 'temperature' movido para dentro de 'options'
            response = ollama.chat(
                model=self.model,
                format="json",
                options={
                    'num_ctx': self.num_ctx,
                    'temperature': self.temperature
                },
                messages=[
                    {'role': 'system', 'content': prompt_sistema},
                    {'role': 'user', 'content': prompt_usuario}
                ]
            )
            evaluation_data = json.loads(response['message']['content'])
            
            if 'nota' in evaluation_data and 'justificativa' in evaluation_data:
                return evaluation_data
            else:
                raise ValueError("A resposta da IA não contém as chaves 'nota' e 'justificativa'.")

        except json.JSONDecodeError:
            return {"nota": 0, "justificativa": "Erro: A IA retornou um formato JSON inválido."}
        except Exception as e:
            print(f"❌ Ocorreu um erro ao chamar a API do Ollama: {e}")
            return {"nota": 0, "justificativa": f"Erro ao avaliar a resposta: {e}"}