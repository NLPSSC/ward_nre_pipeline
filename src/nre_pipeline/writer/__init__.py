from abc import ABC, abstractmethod
from typing import Any, Callable, Dict

from nre_pipeline.models import NLPResult


class NLPResultWriter(ABC):
    """
    Abstract base class for corpus writers that write to files.
    """

    @abstractmethod
    def record(self, nlp_result: NLPResult) -> None:
        """
        Write data to the corpus.

        Args:
            nlp_result: The NLPResult to write
        """
        pass

    @staticmethod
    @abstractmethod
    def create_writer(**kwargs) -> Callable[[], "NLPResultWriter"]:
        raise NotImplementedError("Subclasses must implement this method.")
    

    @abstractmethod
    def writer_details(self) -> Dict[str, Any]:
        raise NotImplementedError("Subclasses must implement this method.")



__all__ = ["NLPResultWriter"]
