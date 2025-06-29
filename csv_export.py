import csv
import io

# O padrão de projeto Builder é usado para construir o relatório CSV passo a passo, onde cada método 
# é responsável por adicionar uma parte específica do relatório.

class csv_export:
    def __init__(self):
        # Usa um buffer de string para construir o CSV em memória
        self.string_buffer = io.StringIO()
        self.writer = csv.writer(self.string_buffer)

    def add_header(self, media_sala: int) -> None:
        self.writer.writerow(['RELATÓRIO DE DESEMPENHO DA TURMA'])
        self.writer.writerow([])
        self.writer.writerow(['ESTATÍSTICAS GERAIS'])
        self.writer.writerow(['Média Geral da Sala', media_sala])
        self.writer.writerow([])
        
    def add_student_grades(self, dados_alunos: list[dict]) -> None:
        self.writer.writerow(['NOTAS INDIVIDUAIS'])
        self.writer.writerow(['Aluno', 'Nota Final'])
        for aluno in dados_alunos:
            self.writer.writerow([aluno.get('nome', 'N/A'), aluno.get('nota', 0)])
        self.writer.writerow([])
        
    def add_statistics(self, taxa_acertos_q: int, taxa_acertos_t: int) -> None:
        self.writer.writerow(['TAXA DE ACERTO POR QUESTÃO (%)'])
        for i, taxa in enumerate(taxa_acertos_q):
            self.writer.writerow([f'Questão {i+1}', taxa])
        self.writer.writerow([])

        self.writer.writerow(['TAXA DE ACERTO POR TEMA (%)'])
        for tema, taxa in taxa_acertos_t.items():
            self.writer.writerow([tema, taxa])
        
    def get_csv_content(self) -> str:
        """Retorna o conteúdo CSV final como uma string."""
        return self.string_buffer.getvalue()