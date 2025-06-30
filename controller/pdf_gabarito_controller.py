# controller/pdf_gabarito_controller.py
import sys, json
from pathlib import Path
from controller.services.answer_key_importer import AnswerKeyImporter

def main() -> None:
    if len(sys.argv) != 2:
        sys.exit("Uso: python controller/pdf_gabarito_controller.py caminho/gabarito.pdf")

    pdf_path = Path(sys.argv[1]).expanduser()
    if not pdf_path.exists():
        sys.exit(f"Arquivo {pdf_path} não encontrado.")

    key = AnswerKeyImporter().import_key(pdf_path)
    print(json.dumps(key, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
