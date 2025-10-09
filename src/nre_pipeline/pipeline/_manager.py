from itertools import cycle
from typing import Callable, List
from nre_pipeline.models import Document, NLPResult
from nre_pipeline.processor import Processor
from nre_pipeline.reader import CorpusReader
from nre_pipeline.writer import NLPResultWriter


def processor_round_robin(processors: List[Processor]) -> Callable[[int], Processor]:
    """Create a round-robin processor selector."""

    def get_processor(index: int) -> Processor:
        return processors[index % len(processors)]

    return get_processor


class PipelineManager:
    def __init__(
        self,
        *,
        num_processor_workers: int,
        processor: Callable[[int], Processor],
        reader: Callable[[], CorpusReader],
        writer: Callable[[], NLPResultWriter],
    ) -> None:
        self._processor_iter: cycle[Processor] = cycle(
            [processor(i) for i in range(num_processor_workers)]
        )
        self._reader: CorpusReader = reader()
        self._writer: NLPResultWriter = writer()

    def __enter__(self):
        # Optional: Add any setup code here
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        # Optional: Add any cleanup code here
        pass

    def run(self) -> None:
        """Run the pipeline."""
        for document in self._reader:
            result: NLPResult = next(self._processor_iter)(document)
            self._writer.record(result)
