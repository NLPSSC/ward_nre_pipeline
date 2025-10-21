from abc import ABC, abstractmethod
import queue
import threading
from typing import Any, Callable, Dict, List


from nre_pipeline.app.interruptible_mixin import InterruptibleMixin
from nre_pipeline.app.thread_loop_mixin import ThreadLoopMixin
from nre_pipeline.app.verbose_mixin import VerboseMixin
from nre_pipeline.models._nlp_result import NLPResultItem
from nre_pipeline.processor._base import QUEUE_EMPTY

DEFAULT_WRITE_BATCH_SIZE = 10


class NLPResultWriter(ABC, InterruptibleMixin, VerboseMixin, ThreadLoopMixin):
    """
    Abstract base class for corpus writers that write to files.
    """

    def __init__(
        self,
        nlp_results_outqueue: queue.Queue,
        user_interrupt: threading.Event,
        **config
    ):
        self._nlp_results_outqueue = nlp_results_outqueue
        self._num_processor_workers = config.get("num_processor_workers", 1)
        super().__init__(user_interrupt=user_interrupt, target=self._writer_loop)

    def _writer_loop(self):
        write_batch = []
        while not self.user_interrupted():
            try:
                nlp_result = self._nlp_results_outqueue.get(timeout=5)
            except queue.Empty:
                continue

            if nlp_result == QUEUE_EMPTY:
                break
            elif isinstance(nlp_result, NLPResultItem):
                write_batch.append(nlp_result)
                if len(write_batch) > DEFAULT_WRITE_BATCH_SIZE:
                    self.record(write_batch)
                    write_batch = []
            else:
                raise RuntimeError("Unexpected item type in writer queue")

        if len(write_batch) > DEFAULT_WRITE_BATCH_SIZE:
            self.record(write_batch)
            write_batch = []

    @abstractmethod
    def record(self, nlp_result: NLPResultItem | List[NLPResultItem]) -> None:
        """
        Write data to the corpus.

        Args:
            nlp_result: The NLPResult to write
        """
        if self.user_interrupted():
            return
        self._record(nlp_result)

    @abstractmethod
    def _record(self, nlp_result: NLPResultItem | List[NLPResultItem]) -> None:
        pass

    @staticmethod
    def create_writer(**kwargs) -> Callable[[], "NLPResultWriter"]:
        raise NotImplementedError("Subclasses must implement this method.")

    @abstractmethod
    def writer_details(self) -> Dict[str, Any]:
        raise NotImplementedError("Subclasses must implement this method.")


__all__ = ["NLPResultWriter"]
