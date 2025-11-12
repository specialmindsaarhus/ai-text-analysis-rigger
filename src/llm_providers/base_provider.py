from abc import ABC, abstractmethod
from typing import Dict, List


class BaseLLMProvider(ABC):
    """
    Abstrakt base class for LLM providers.
    Gør det nemt at skifte mellem forskellige AI services.
    """

    def __init__(self, api_key: str):
        self.api_key = api_key

    @abstractmethod
    def analyze_text(self, text: str, parameters: Dict[str, bool]) -> Dict[str, any]:
        """
        Analyserer tekst og returnerer rettelser og feedback.

        Args:
            text: Teksten der skal analyseres
            parameters: Dict med analyse parametre (grammatik, stavning, etc.)

        Returns:
            Dict med:
                - original_text: Original tekst
                - corrected_text: Rettet tekst
                - corrections: Liste af rettelser
                - feedback: Generel feedback
        """
        pass

    @abstractmethod
    def get_provider_name(self) -> str:
        """Returnerer navnet på provideren"""
        pass
