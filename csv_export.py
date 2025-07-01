import csv
import io

# O padrão Builder é usado para construir o relatório CSV passo a passo.
class csv_export:
    def __init__(self):
        # Usa um buffer de string para construir o CSV em memória
        self.string_buffer = io.StringIO()
        self.writer = csv.writer(self.string_buffer)

    def adicionaHeader(self) -> None:
        """Adiciona um cabeçalho simples ao relatório."""
        self.writer.writerow(['RELATÓRIO DE DESEMPENHO DA TURMA'])
        self.writer.writerow([])
        
    def adicionaNotasEstudantes(self, dados_alunos: list[dict]) -> None:
        """Adiciona as notas individuais dos alunos."""
        self.writer.writerow(['NOTAS INDIVIDUAIS'])
        self.writer.writerow(['Aluno', 'Nota Final'])
        for aluno in dados_alunos:
            # Procura pela nota em 'nota' ou 'nota_total' para maior compatibilidade
            nota = aluno.get('nota', aluno.get('nota_total', 0))
            self.writer.writerow([aluno.get('nome', 'N/A'), nota])
        self.writer.writerow([])
        
    def adicionaEstatisticas(self, taxa_acertos_q: list, taxa_acertos_t: dict) -> None:
        """Adiciona estatísticas detalhadas de acertos (opcional)."""
        self.writer.writerow(['TAXA DE ACERTO POR QUESTÃO (%)'])
        for i, taxa in enumerate(taxa_acertos_q):
            self.writer.writerow([f'Questão {i+1}', taxa])
        self.writer.writerow([])

        self.writer.writerow(['TAXA DE ACERTO POR TEMA (%)'])
        for tema, taxa in taxa_acertos_t.items():
            self.writer.writerow([tema, taxa])
        
    def getConteudoCsv(self) -> str:
        """Retorna o conteúdo CSV final como uma string."""
        return self.string_buffer.getvalue()