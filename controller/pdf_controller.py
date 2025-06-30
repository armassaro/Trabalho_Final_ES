# controllers/pdf_controller.py
import sys, json
from pathlib import Path
from services.quiz_importer import QuizImporter
from parsers.default_parser import DefaultParser

def main() -> None:
    if len(sys.argv) != 2:
        sys.exit("Uso: python pdf_controller.py caminho/para/prova.pdf")

    pdf_path = Path(sys.argv[1]).expanduser()
    if not pdf_path.exists():
        sys.exit(f"Arquivo {pdf_path} não encontrado.")

    importer = QuizImporter(DefaultParser())
    prova = importer.parse_pdf(pdf_path)

    # Aqui você faria: salvar no BD, renderizar View, etc.
    print(json.dumps(prova, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
