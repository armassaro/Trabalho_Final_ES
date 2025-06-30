import matplotlib.pyplot as plt, stats as st
from abc import ABC, abstractmethod
from typing import List, Dict
from matplotlib.backends.backend_pdf import PdfPages

#############--- FactoryMethod das funções gráficas ---#############
class GraficoFactory(ABC):
    @abstractmethod
    def criar_grafico(self, tipo: str):
        pass

class GraficoFactoryConcreta(GraficoFactory):
    def criar_grafico(self, tipo: str):
        graficos = {
            "graf_acertos_por_questao": graf_acertos_por_questao,
            "graf_acertos_por_tema": graf_acertos_por_tema,
            "graf_notas_totais": graf_notas_totais,
            "graf_percentual_aprovados": graf_percentual_aprovados
        }

        try:
            return graficos[tipo]
        except KeyError:
            raise ValueError(f"Tipo de gráfico '{tipo}' inválido.")

#############--- Funções de geração de gráfico ---#############        
def graf_acertos_por_questao(num_questoes: int, taxa_questao: List[float]):  
    # Barra vertical de taxa de acertos por questão
    plt.figure()
    plt.bar(range(1, num_questoes+1), taxa_questao)
    plt.title("Taxa de Acertos por Questão (%)")
    plt.xlabel("Questão")
    plt.ylabel("Taxa de Acertos (%)")

def graf_acertos_por_tema(taxa_tema: dict):
    # Barra vertical de taxa de acertos por tema
    temas = list(taxa_tema.keys())
    valores_tema = list(taxa_tema.values())
    
    plt.figure()
    plt.bar(temas, valores_tema)
    plt.title("Taxa de Acertos por Tema (%)")
    plt.xlabel("Tema")
    plt.ylabel("Taxa de Acertos (%)")
    plt.xticks(rotation=45)  
    plt.tight_layout()       

def graf_notas_totais(notas_totais: List[float], nota_aprovacao: float):
    # Histograma das notas totais com linhas de média e aprovação
    num_alunos = len(notas_totais)
    media_sala = sum(notas_totais) / num_alunos
    plt.figure()
    plt.hist(notas_totais, bins=range(0, max(notas_totais)+2), edgecolor='black')
    plt.axvline(media_sala, linestyle='--')
    plt.axvline(nota_aprovacao, linestyle='--')
    plt.title("Histograma de Notas Totais")
    plt.xlabel("Nota Total")
    plt.ylabel("Número de Alunos")

def graf_percentual_aprovados(aprovados: int, reprovados: int):
    # Gráfico de pizza com percentual de aprovados vs reprovados
    plt.figure()
    plt.pie([aprovados, reprovados], labels=["Aprovados", "Reprovados"], autopct='%1.1f%%')
    plt.title("Percentual de Aprovados vs Reprovados")

#############--- Geração do relatório em PDF---#############
def gerarPDF(notas: List[List[float]], tags: List[List[float]], nota_aprovacao: float):
    Rfactory = st.RelatorioFactoryConcreta()

    num_questoes, taxa_questao = Rfactory.criar_relatorio("taxa_acertos_questao")(notas)
    taxa_tema = Rfactory.criar_relatorio("taxa_acertos_tema")(notas, tags)
    notas_totais = Rfactory.criar_relatorio("notas_totais")(notas)
    aprovados, reprovados = Rfactory.criar_relatorio("taxa_aprovacao")(notas, nota_aprovacao)

    Gfactory = GraficoFactoryConcreta()

    with PdfPages("relatorio_graficos.pdf") as pdf:
        g1 = Gfactory.criar_grafico("graf_acertos_por_questao")(num_questoes, taxa_questao)
        pdf.savefig(g1)
        plt.close(g1)

        g2 = Gfactory.criar_grafico("graf_acertos_por_tema")(taxa_tema)
        pdf.savefig(g2)
        plt.close(g2)

        g3 = Gfactory.criar_grafico("graf_notas_totais")(notas_totais, nota_aprovacao)
        pdf.savefig(g3)
        plt.close(g3)

        g4 = Gfactory.criar_grafico("graf_percentual_aprovados")(aprovados, reprovados)
        pdf.savefig(g4)
        plt.close(g4)


#######--- Exemplo (apagar quando integrado) ---########

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

    gerarPDF(notas, tags, nota_aprovacao)


