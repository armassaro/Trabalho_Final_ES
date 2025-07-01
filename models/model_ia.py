from abc import ABC, abstractmethod
import ollama
import re
import json
from typing import Dict, List, Optional, Union

class EstrategiaCorrecao(ABC):
    @abstractmethod
    def gerar_gabarito(self, pergunta: str, alternativas: Optional[List[str]] = None) -> str:
        pass
    
    @abstractmethod
    def corrigir(self, resposta_aluno: str, resposta_gabarito: str, pontos: float) -> Dict[str, Union[float, str]]:
        pass

class CorrecaoObjetiva(EstrategiaCorrecao):
    def gerar_gabarito(self, pergunta: str, alternativas: Optional[List[str]] = None) -> str:
        prompt = f"""
        Para a questão objetiva abaixo, responda APENAS com a letra da alternativa correta (A, B, C, etc.)
        
        Pergunta: {pergunta}
        Alternativas:
        {chr(10).join(alternativas) if alternativas else 'Nenhuma alternativa fornecida'}
        """
        
        response = ollama.generate(
            model='phi3:mini',
            prompt=prompt,
            options={'temperature': 0}  # Determinístico
        )
        
        match = re.search(r'[A-E]', response['response'].upper())
        return match.group(0) if match else 'A'

    def corrigir(self, resposta_aluno: str, resposta_gabarito: str, pontos: float) -> Dict[str, Union[float, str]]:
        correta = resposta_aluno.upper() == resposta_gabarito.upper()
        return {
            'nota': pontos if correta else 0,
            'feedback': f"Resposta {'correta' if correta else 'incorreta'} (Esperado: {resposta_gabarito})"
        }

class CorrecaoDissertativa(EstrategiaCorrecao):
    def gerar_gabarito(self, pergunta: str, alternativas: Optional[List[str]] = None) -> str:
        prompt = f"""
        Gere uma resposta modelo concisa (máximo 2 linhas) para:
        {pergunta}
        """
        
        response = ollama.generate(
            model='phi3:mini',
            prompt=prompt,
            options={'temperature': 0.1}
        )
        
        return response['response'].strip()

    def corrigir(self, resposta_aluno: str, resposta_gabarito: str, pontos: float) -> Dict[str, Union[float, str]]:
        prompt = f"""
        Avalie a resposta do aluno considerando o gabarito oficial.
        Retorne APENAS um JSON com: {{"nota": float, "feedback": str}}
        
        Pergunta: [Redacted]
        Gabarito: {resposta_gabarito}
        Resposta do aluno: {resposta_aluno}
        Pontuação máxima: {pontos}
        """
        
        try:
            response = ollama.generate(
                model='phi3:mini',
                prompt=prompt,
                options={'temperature': 0.1}
            )
            data = json.loads(response['response'])
            return {
                'nota': min(float(data['nota']), pontos),
                'feedback': data['feedback']
            }
        except:
            # Fallback simples
            similar = len(set(resposta_aluno.lower().split()) & set(resposta_gabarito.lower().split())) / \
                     max(len(set(resposta_gabarito.lower().split())), 1)
            return {
                'nota': similar * pontos,
                'feedback': f"Similaridade: {similar*100:.1f}% com o gabarito"
            }

class IAModel:
    def __init__(self):
        self.estrategias = {
            'objetiva': CorrecaoObjetiva(),
            'dissertativa': CorrecaoDissertativa()
        }
    
    def gerar_gabarito(self, questao: Dict) -> str:
        estrategia = self.estrategias[questao['tipo']]
        alternativas = None
        if questao['tipo'] == 'objetiva':
            alternativas = [f"{k}) {v}" for k, v in questao['alternativas'].items()]
        return estrategia.gerar_gabarito(questao['pergunta'], alternativas)
    
    def corrigir(self, questao: Dict, resposta_aluno: str, resposta_gabarito: str) -> Dict[str, Union[float, str]]:
        return self.estrategias[questao['tipo']].corrigir(
            resposta_aluno,
            resposta_gabarito,
            questao['pontos']
        )