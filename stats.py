from abc import ABC, abstractmethod
from typing import List, Dict

#########--- Factory Method ---########

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
            "media_sala": gerar_media_sala,
            "taxa_aprovacao": gerar_taxa_aprovacao
        }

        try:
            return relatorios[tipo]
        except KeyError:
            raise ValueError(f"Tipo de relatório '{tipo}' inválido.")


########--- Cálculos de Estatística ---#########

def gerar_notas_totais(matriz_notas: List[List[float]]) -> List[float]:
    return [sum(aluno) for aluno in matriz_notas]

def gerar_taxa_acertos_por_questao(matriz_notas: List[List[float]]) -> List[float]:
    num_alunos = len(matriz_notas)
    num_questoes = len(matriz_notas[0])
    return [
        round(sum(matriz_notas[i][j] for i in range(num_alunos)) / num_alunos * 100, 2)
        for j in range(num_questoes)
    ]

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

def gerar_media_sala(matriz_notas: List[List[float]]) -> float:
    notas_totais = gerar_notas_totais(matriz_notas)
    return round(sum(notas_totais) / len(notas_totais), 2)

def gerar_taxa_aprovacao(matriz_notas: List[List[float]], nota_aprovacao: float) -> Dict[str, float]:
    notas_totais = gerar_notas_totais(matriz_notas)
    num_alunos = len(notas_totais)
    acima = sum(1 for n in notas_totais if n >= nota_aprovacao)
    abaixo = num_alunos - acima

    return {
        "aprovados (%)": round(acima / num_alunos * 100, 2),
        "reprovados (%)": round(abaixo / num_alunos * 100, 2)
    }

#######--- Exemplo ---########

if __name__ == "__main__":
    # Matriz de notas
    notas = [
        [1, 0, 1, 1],
        [1, 1, 0, 1],
        [0, 1, 0, 0],
        [1, 1, 1, 1]
    ]

    # Matriz de tags
    tags = [
        ["Matemática"],
        ["Matemática", "Geometria"],
        ["Português"],
        ["Matemática"]
    ]

    nota_aprovacao = 3

    factory = RelatorioFactoryConcreta()

    print("Notas totais por aluno:")
    print(factory.criar_relatorio("notas_totais")(notas))

    print("\nTaxa de acertos por questão (%):")
    print(factory.criar_relatorio("taxa_acertos_questao")(notas))

    print("\nTaxa de acertos por tema (%), ordenado crescente:")
    print(factory.criar_relatorio("taxa_acertos_tema")(notas, tags))

    print("\nMédia da sala:")
    print(factory.criar_relatorio("media_sala")(notas))

    print("\nTaxa de aprovação e reprovação (%):")
    print(factory.criar_relatorio("taxa_aprovacao")(notas, nota_aprovacao))
