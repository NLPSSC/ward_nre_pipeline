from abc import ABC, abstractmethod

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


__all__ = [
    "NLPResultWriter",
]
