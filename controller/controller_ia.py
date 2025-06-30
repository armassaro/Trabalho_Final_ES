import ollama
import json

class ControllerIA:
    def __init__(self, model: str = "phi3:mini", temperature: float = 0.1, num_ctx: int = 2048):
        self.model = model
        self.temperature = temperature
        self.num_ctx = num_ctx

    def gerar_gabarito_dissertativo(self, pergunta: str) -> str:
        """
        Gera um gabarito detalhado para uma pergunta dissertativa.

        Args:
            pergunta (str): A pergunta dissertativa para a qual o gabarito será criado.

        Returns:
            str: O gabarito detalhado gerado pela IA.
        """
        print(f"🧠 Gerando gabarito para a pergunta: '{pergunta}'...")

        # O prompt do sistema define o "papel" da IA
        prompt_sistema = """
        Você é um professor especialista e um assistente de avaliação.
        Sua tarefa é criar um gabarito detalhado e bem estruturado para a pergunta dissertativa fornecida.
        O gabarito deve destacar os pontos-chave, conceitos essenciais, argumentos esperados e, se aplicável,
        exemplos que constituiriam uma resposta completa e de alta qualidade.
        Este gabarito será usado como base para avaliar as respostas dos alunos de forma objetiva.
        """

        try:
            response = ollama.chat(
                model=self.model,
                temperature=self.temperature,
                options={'num_ctx': self.num_ctx},
                messages=[
                    {'role': 'system', 'content': prompt_sistema},
                    {'role': 'user', 'content': f"Gere o gabarito para a seguinte pergunta: {pergunta}"}
                ]
            )
            return response['message']['content']
        except Exception as e:
            print(f"❌ Ocorreu um erro ao chamar a API do Ollama: {e}")
            return "Erro ao gerar o gabarito."

    def avaliar_resposta_aluno(self, pergunta: str, gabarito: str, resposta_aluno: str, nota_maxima: int = 10) -> dict:

        # Prompt do sistema mais complexo para a tarefa de avaliação
        prompt_sistema = f"""
        Você é um assistente de avaliação rigoroso, justo e objetivo.
        Sua tarefa é analisar a resposta de um aluno, compará-la com o gabarito oficial e atribuir uma nota de 0 a {nota_maxima}.

        Siga estas etapas com atenção:
        1. Leia a 'Pergunta Original' para entender o que foi solicitado.
        2. Estude o 'Gabarito (Resposta Ideal)' para saber quais são os critérios de uma resposta perfeita.
        3. Analise cuidadosamente a 'Resposta do Aluno'.
        4. Compare a 'Resposta do Aluno' com o 'Gabarito'. Identifique os pontos-chave que o aluno acertou, os que abordou parcialmente e os que omitiu.
        5. Com base na sua análise comparativa, atribua uma nota numérica. A nota deve refletir o quão próxima a resposta do aluno está do gabarito.
        6. Escreva uma 'justificativa' clara e construtiva, explicando o porquê da nota atribuída. Mencione os pontos fortes e as áreas que precisam de melhoria na resposta do aluno.
        7. Retorne sua avaliação estritamente no formato JSON, com as chaves "nota" (um número) e "justificativa" (um texto). Não adicione nenhum texto antes ou depois do JSON.

        Exemplo de saída esperada:
        {{
          "nota": 8.5,
          "justificativa": "O aluno demonstrou um bom entendimento sobre o ciclo da água, descrevendo corretamente a evaporação e a precipitação. No entanto, não mencionou a importância da condensação e da transpiração das plantas, que são pontos relevantes do gabarito. A nota reflete a cobertura parcial dos tópicos essenciais."
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

        try:
            response = ollama.chat(
                model=self.model,
                temperature=self.temperature,
                format="json", # Instruindo o Ollama a forçar a saída em JSON
                options={'num_ctx': self.num_ctx},
                messages=[
                    {'role': 'system', 'content': prompt_sistema},
                    {'role': 'user', 'content': prompt_usuario}
                ]
            )

            # O conteúdo da mensagem já deve ser um objeto JSON se format="json" funcionar
            # A biblioteca Ollama lida com o parse do JSON automaticamente nesse caso.
            evaluation_data = json.loads(response['message']['content'])

            # Validação simples do dicionário retornado
            if 'nota' in evaluation_data and 'justificativa' in evaluation_data:
                return evaluation_data
            else:
                raise ValueError("A resposta da IA não contém as chaves 'nota' e 'justificativa'.")

        except json.JSONDecodeError:
            return {"nota": 0, "justificativa": "Erro: A IA retornou um formato inválido que não pôde ser processado como JSON."}
        except Exception as e:
            print(f"❌ Ocorreu um erro ao chamar a API do Ollama: {e}")
            return {"nota": 0, "justificativa": f"Erro ao avaliar a resposta: {e}"}