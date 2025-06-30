import ollama
import json
import re
from typing import Dict, Union

class IAModel:
    def __init__(self, model: str = "phi3:mini", temperature: float = 0.1, num_ctx: int = 2048):
        self.model = model
        self.temperature = temperature
        self.num_ctx = num_ctx

    def gerarRespostaGabarito(self, pergunta: str) -> str:
        """Gera resposta modelo para uma pergunta dissertativa"""
        try:
            response = ollama.generate(  # Mudado para generate() em vez de chat()
                model=self.model,
                prompt=f"Gere um gabarito modelo para a pergunta: {pergunta}",
                options={
                    'temperature': self.temperature,
                    'num_ctx': self.num_ctx
                }
            )
            return response['response']
        except Exception as e:
            print(f"Erro ao gerar gabarito: {str(e)}")
            return "Resposta não disponível"

    def avaliar_resposta_aluno(self, pergunta: str, gabarito: str, resposta_aluno: str, nota_maxima: int = 10) -> Dict[str, Union[float, str]]:
        """Avalia a resposta do aluno retornando nota e feedback"""
        prompt = f"""
        Avalie esta resposta de aluno considerando:
        - Pergunta: {pergunta}
        - Gabarito: {gabarito}
        - Resposta do aluno: {resposta_aluno}
        
        Retorne um JSON com: {{"nota": float, "feedback": str}}
        A nota deve ser entre 0 e {nota_maxima}.
        """
        
        try:
            response = ollama.generate(
                model=self.model,
                prompt=prompt,
                options={
                    'temperature': self.temperature,
                    'num_ctx': self.num_ctx
                }
            )
            
            # Parse seguro da resposta
            response_text = response['response']
            print("Resposta da IA:", response_text)  # Debug: Exibir resposta da IA
            try:
                data = json.loads(response_text)
                if isinstance(data, dict):
                    nota = min(float(data.get("nota", 0)), float(nota_maxima))
                    feedback = data.get("feedback", "Sem feedback detalhado")
                    return {"nota": nota, "feedback": feedback}
            except json.JSONDecodeError:
                # Fallback para respostas não JSON
                if any(word in response_text.lower() for word in ["excelente", "bom", "correto"]):
                    return {"nota": nota_maxima * 0.9, "feedback": response_text}
                return {"nota": 0, "feedback": response_text}
                
        except Exception as e:
            print(f"Erro na avaliação: {str(e)}")
        
        return {"nota": 0, "feedback": "Erro na avaliação"}

    @staticmethod
    def validarNota(novo_valor, valor_max_str):
        """Valida se uma nota está dentro do intervalo permitido"""
        try:
            valor_max = float(valor_max_str)
            nota = float(novo_valor) if novo_valor else 0
            return 0 <= nota <= valor_max
        except ValueError:
            return False