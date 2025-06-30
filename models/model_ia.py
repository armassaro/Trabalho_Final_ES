# model.py

import ollama
import json
import re
from typing import Union

class IAModel:
    def __init__(self, model: str = "phi3:mini", temperature: float = 0.1, num_ctx: int = 2048):
        self.model = model
        self.temperature = temperature
        self.num_ctx = num_ctx

    def gerar_gabarito_dissertativo(self, pergunta: str) -> str:
        prompt_sistema = """
            Criar um gabarito detalhado e bem estruturado para a pergunta dissertativa fornecida.
            O gabarito deve destacar os pontos-chave, conceitos essenciais e argumentos esperados.
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
            return f"Erro ao comunicar com o modelo de IA: {e}"

    def avaliar_resposta_aluno(self, pergunta: str, gabarito: str, resposta_aluno: str, nota_maxima: int = 10) -> float:
        prompt_sistema = f"""
        Sua tarefa é analisar a resposta de um aluno,
        compará-la com o gabarito e atribuir uma nota de 0 a {nota_maxima}.
        Retorne sua avaliação estritamente no formato de um objeto JSON, com apenas a chave "nota".
        Exemplo de saída: {{"nota": 8.5}}
        """
        prompt_usuario = f"""
        ---
        **Pergunta Original:**\n{pergunta}
        ---
        **Gabarito (Resposta Ideal):**\n{gabarito}
        ---
        **Resposta do Aluno para Avaliar:**\n{resposta_aluno}
        ---
        """
        try:
            response = ollama.chat(
                model=self.model,
                temperature=self.temperature,
                options={'num_ctx': self.num_ctx},
                messages=[
                    {'role': 'system', 'content': prompt_sistema},
                    {'role': 'user', 'content': prompt_usuario}
                ]
            )
            response_content = response['message']['content']
            match = re.search(r'\{.*\}', response_content, re.DOTALL)
            
            if match:
                json_string = match.group(0)
                evaluation_data = json.loads(json_string)
            else:
                evaluation_data = json.loads(response_content)

            if 'nota' in evaluation_data:
                return float(evaluation_data['nota'])
            return 0.0
        except (json.JSONDecodeError, Exception):
            return 0.0