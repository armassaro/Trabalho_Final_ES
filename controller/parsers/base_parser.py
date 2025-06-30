# parsers/base_parser.py
from abc import ABC, abstractmethod
from typing import Dict

class BaseParser(ABC):
    """Interface de estratégia: todas as classes concretas devem implementar parse()."""

    @abstractmethod
    def parse(self, raw_text: str) -> Dict:
        """Recebe o texto bruto do PDF e devolve um dicionário estruturado."""
