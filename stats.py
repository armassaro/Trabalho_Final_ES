from abc import ABC, abstractmethod
from typing import List, Dict

#######--- FactoryMethod das funções estatísticas---########

class RelatorioFactory(ABC):
    @abstractmethod
    def criar_relatorio(self, tipo: str):
        pass

class RelatorioFactoryConcreta(RelatorioFactory):
    def criar_relatorio(self, tipo: str):
        relatorios = {
            "notas_totais": gerar_notas_totais,
            "taxa_acertos_questao": gerar_taxa_acertos_por_questao,
            "taxa_acertos_tema": gerar_taxa_acertos_por_tema,
            "taxa_aprovacao": gerar_taxa_aprovacao
        }

        try:
            return relatorios[tipo]
        except KeyError:
            raise ValueError(f"Tipo de relatório '{tipo}' inválido.")


#######--- Funções estatísticas---########

def gerar_notas_totais(matriz_notas: List[List[float]]) -> List[float]:
    return [sum(aluno) for aluno in matriz_notas]

def gerar_taxa_acertos_por_questao(matriz_notas: List[List[float]]) -> List[float]:
    num_alunos = len(matriz_notas)
    num_questoes = len(matriz_notas[0])
    taxa_questao = [
        round(sum(matriz_notas[i][j] for i in range(num_alunos)) / num_alunos * 100, 2)
        for j in range(num_questoes)
    ]
    return num_questoes, taxa_questao

def gerar_taxa_acertos_por_tema(matriz_notas: List[List[float]], matriz_tags: List[List[str]]) -> Dict[str, float]:
    tema_acertos = {}
    tema_total = {}

    num_alunos = len(matriz_notas)
    num_questoes = len(matriz_notas[0])

    for j in range(num_questoes):
        for tag in matriz_tags[j]:
            tema_acertos[tag] = tema_acertos.get(tag, 0) + sum(matriz_notas[i][j] for i in range(num_alunos))
            tema_total[tag] = tema_total.get(tag, 0) + num_alunos

    taxa = {tema: round(tema_acertos[tema] / tema_total[tema] * 100, 2) for tema in tema_acertos}
    return dict(sorted(taxa.items(), key=lambda item: item[1]))

def gerar_taxa_aprovacao(matriz_notas: List[List[float]], nota_aprovacao: float) -> Dict[str, float]:
    notas_totais = gerar_notas_totais(matriz_notas)
    num_alunos = len(notas_totais)
    acima = sum(1 for n in notas_totais if n >= nota_aprovacao)
    abaixo = num_alunos - acima

    return acima, abaixo

