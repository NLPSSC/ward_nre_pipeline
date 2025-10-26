from datetime import datetime
import os
from pathlib import Path
import queue
from abc import abstractmethod
from typing import Any, Callable, Dict, List, Union, cast
from loguru import logger
from nre_pipeline.app.verbose_mixin import VerboseMixin
from nre_pipeline.common.base._component_base import _BaseProcess
from nre_pipeline.common.base._consts import QUEUE_EMPTY, TQueueEmpty
from nre_pipeline.models._nlp_result import NLPResultItem
from nre_pipeline.writer import NUMBER_DOCS_TO_WRITE_BEFORE_YIELD


class NLPResultWriter(_BaseProcess, VerboseMixin):
    """
    Abstract base class for corpus writers that write to files.
    """

    def __init__(
        self,
        outqueue: queue.Queue,
        total_written,
        process_counter,
        output_path: str | None = None,
        **config,
    ):
        self._outqueue: queue.Queue[NLPResultItem | TQueueEmpty] = outqueue
        self._total_written = total_written
        self._process_counter = process_counter
        self._output_path: str = self._build_output_path(output_path)

        super().__init__()

    @property
    def output_path(self) -> str:
        return self._output_path

    def _build_output_path(self, output_path) -> str:
        output_folder: Path = (
            Path(self._get_output_path(output_path)) / self._output_subfolder()
        )
        output_folder.mkdir(exist_ok=True)
        return str(output_folder / self._build_output_file_name())

    @abstractmethod
    def _output_subfolder(self) -> str:
        raise NotImplementedError("Must implement _output_subfolder")

    @abstractmethod
    def _build_output_file_name(self) -> str:
        raise NotImplementedError("Must implement _build_output_file_name")

    @property
    def total_written(self):
        return self._total_written

    def _get_output_path(self, db_path: str | None) -> str:
        _path = db_path or os.getenv("OUTPUT_ROOT_PATH", None)
        if _path is None or os.path.isdir(_path) is False:
            raise ValueError(
                "Output path must be provided either as an argument or via the OUTPUT_ROOT_PATH environment variable."
            )
        return cast(str, _path)

    def update_total_written(self, current_total_written: int):
        new_total = self._total_written.get() + current_total_written
        self._total_written.set(new_total)

    @classmethod
    def create(cls, manager, **config):
        _outqueue = config.get("outqueue")
        if _outqueue is None:
            raise ValueError("Outqueue must be provided.")
        outqueue: queue.Queue[NLPResultItem | TQueueEmpty] = cast(
            queue.Queue[NLPResultItem | TQueueEmpty], _outqueue
        )
        total_written = manager.Value("i", 0)
        config["outqueue"] = outqueue
        config["total_written"] = total_written
        config["process_counter"] = config.get("process_counter")
        config["all_processes_complete_barrier"] = config.get(
            "all_processes_complete_barrier"
        )
        return cls(**config)

    def _get_results_id(self) -> str:
        return datetime.now().strftime("%Y_%m_%d_%H_%M_%S")

    def get_process_name(self) -> str:
        return f"{self.__class__.__name__}"

    def _runner(self):
        queue_empty_set = False
        try:
            write_batch = []
            while True:

                try:
                    nlp_result = self._outqueue.get(timeout=1)
                    # logger.debug("_thread_worker for {}", self.__class__.__name__)
                    queue_empty_set = nlp_result == QUEUE_EMPTY

                except queue.Empty:
                    if queue_empty_set and self._process_counter.get() == 0:
                        logger.info("Received QUEUE_EMPTY sentinel")
                        break
                    continue

                if isinstance(nlp_result, NLPResultItem):
                    write_batch.append(nlp_result)
                    if len(write_batch) >= NUMBER_DOCS_TO_WRITE_BEFORE_YIELD:
                        self.record(write_batch)
                        write_batch = []

            if write_batch:
                self.record(write_batch)
                write_batch = []
        except Exception as e:
            logger.error(f"Error occurred while recording NLP results: {e}")
            pass
        finally:
            self._on_write_complete()

    @abstractmethod
    def _on_write_complete(self):
        raise NotImplementedError("Subclasses must implement _on_write_complete.")

    def record(self, nlp_result: Union[NLPResultItem, List[NLPResultItem]]) -> None:
        """
        Write data to the corpus.

        Args:
            nlp_result: The NLPResult to write
        """
        self._record(nlp_result)

    @abstractmethod
    def _record(self, nlp_result: Union[NLPResultItem, List[NLPResultItem]]) -> None:
        pass

    @staticmethod
    def create_writer(**kwargs) -> Callable[[], "NLPResultWriter"]:
        raise NotImplementedError("Subclasses must implement this method.")

    @abstractmethod
    def writer_details(self) -> Dict[str, Any]:
        raise NotImplementedError("Subclasses must implement this method.")


#################################################################################
# Initialization strategy for persistance
#################################################################################
# init_strategy: _InitStrategy | None = None,
