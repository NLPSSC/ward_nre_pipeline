import threading
from abc import ABC, abstractmethod
from typing import Any, Generator, List

from loguru import logger

from nre_pipeline.interruptible_mixin import InterruptibleMixin
from nre_pipeline.models import NLPResult
from nre_pipeline.models._batch import DocumentBatch
from nre_pipeline.processor._not_available_ex import ProcessorNotAvailable
from tqdm import tqdm
from tkinter import Tk, Toplevel, Label, StringVar
import time


class Processor(ABC, InterruptibleMixin):
    def __init__(self, processor_id: int, user_interrupt=None) -> None:
        super().__init__()
        self._index = processor_id
        self._queue = None
        self._available_for_processing = True
        self._lock = threading.Lock()

    def __str__(self):
        return f"[{self.__class__.__name__}] [{self._index}]"

    def __repr__(self) -> str:
        availability = "available" if self._available_for_processing else "busy"
        return f"{super().__str__()} ({availability})"

    @property
    def available_for_processing(self) -> bool:
        with self._lock:
            return self._available_for_processing

    def __call__(self, document_batch: DocumentBatch):
        """Process a document and return the result."""
        with self._lock:
            if self._available_for_processing is False:
                raise ProcessorNotAvailable(self)
            self._available_for_processing = False

        def task():
            threading.current_thread().name = (
                f"Processing Batch #{document_batch.batch_id}"
            )
            logger.debug(
                f"Processor {self} is processing batch {document_batch.batch_id}"
            )
            if self.user_interrupted():
                logger.warning(f"Processor {self} interrupted by user.")
                self._available_for_processing = True
                return
            nlp_results: List[NLPResult] = list(monitor_call(document_batch))
            assert self._queue is not None
            self._queue.put(nlp_results)
            self._available_for_processing = True

        def monitor_call(_document_batch):
            results = []
            # Create a simple Tkinter progress dialog
            root = Tk()
            root.withdraw()  # Hide the main window

            progress_win = Toplevel(root)
            progress_win.title(f"Processing Batch #{document_batch.batch_id}")
            progress_var = StringVar()
            progress_label = Label(progress_win, textvariable=progress_var, width=40)
            progress_label.pack(padx=20, pady=20)

            results = []
            total = sum(1 for _ in self._call(_document_batch))
            progress_win.update()

            # Re-run generator since we exhausted it for counting
            for idx, result in enumerate(self._call(_document_batch), 1):
                results.append(result)
                progress_var.set(f"Processing {idx}/{total}")
                progress_win.update()
                time.sleep(0.01)  # Small delay to allow UI update

            progress_win.destroy()
            root.quit()
            return results

        thread = threading.Thread(target=task)
        thread.start()

    @abstractmethod
    def _call(self, document_batch: DocumentBatch) -> Generator[NLPResult, Any, None]:
        """Process a document and return the result."""
        raise NotImplementedError("Subclasses must implement this method.")
