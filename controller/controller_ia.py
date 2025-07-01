import os
from typing import List, Dict
from models.model_ia import IAModel

class ControllerIA:
    def __init__(self):
        self.ia = IAModel()
        self.gabarito_path = "gabarito.txt"
    
    def gerar_gabarito(self, questoes: List[Dict], salvar: bool = True) -> List[str]:
        gabarito = []
        for q in questoes:
            resposta = self.ia.gerar_gabarito(q)
            gabarito.append(resposta)
        
        if salvar:
            self._salvar_gabarito(gabarito)
        return gabarito
    
    def _salvar_gabarito(self, gabarito: List[str]):
        with open(self.gabarito_path, 'w', encoding='utf-8') as f:
            for i, resp in enumerate(gabarito, 1):
                f.write(f"{i}-{resp}\n")
    
    def carregar_gabarito(self) -> List[str]:
        if not os.path.exists(self.gabarito_path):
            return []
        
        with open(self.gabarito_path, 'r', encoding='utf-8') as f:
            return [linha.split('-', 1)[1].strip() for linha in f if '-' in linha]
    
    def corrigir_prova(self, aluno: Dict, questoes: List[Dict], gabarito: List[str]) -> Dict:
        resultado = {
            'nome': aluno['nome'],
            'nota_total': 0,
            'questoes': []
        }
        
        for i, (questao, resp_gabarito) in enumerate(zip(questoes, gabarito)):
            if i >= len(aluno['respostas']):
                break
                
            correcao = self.ia.corrigir(
                questao,
                aluno['respostas'][i],
                resp_gabarito
            )
            
            resultado['nota_total'] += correcao['nota']
            resultado['questoes'].append({
                'numero': questao['numero'],
                'nota': correcao['nota'],
                'feedback': correcao['feedback']
            })
        
        return resultado