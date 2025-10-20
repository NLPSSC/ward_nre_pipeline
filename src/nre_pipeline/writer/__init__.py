from abc import ABC, abstractmethod
import threading
from typing import Any, Callable, Dict, List


from nre_pipeline.app.interruptible_mixin import InterruptibleMixin
from nre_pipeline.models._nlp_result import NLPResultFeatures


class NLPResultWriter(ABC, InterruptibleMixin):
    """
    Abstract base class for corpus writers that write to files.
    """

    def __init__(self, user_interrupt: threading.Event, **config):
        self._num_processor_workers = config.get("num_processor_workers", 1)
        super().__init__(user_interrupt=user_interrupt)

    @abstractmethod
    def record(self, nlp_result: NLPResultFeatures | List[NLPResultFeatures]) -> None:
        """
        Write data to the corpus.

        Args:
            nlp_result: The NLPResult to write
        """
        if self.user_interrupted():
            return
        self._record(nlp_result)

    @abstractmethod
    def _record(self, nlp_result: NLPResultFeatures | List[NLPResultFeatures]) -> None:
        pass

    @staticmethod
    def create_writer(**kwargs) -> Callable[[], "NLPResultWriter"]:
        raise NotImplementedError("Subclasses must implement this method.")

    @abstractmethod
    def writer_details(self) -> Dict[str, Any]:
        raise NotImplementedError("Subclasses must implement this method.")


__all__ = ["NLPResultWriter"]
