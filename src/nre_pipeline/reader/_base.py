from abc import ABC, abstractmethod
from typing import Any, Callable, Iterator

from nre_pipeline.models import Document
from nre_pipeline.models._batch import DocumentBatch


class CorpusReader(ABC):
    """
    Abstract base class for corpus readers that iterate over files.
    """

    @staticmethod
    @abstractmethod
    def create_reader(**kwargs) -> Callable[[], "CorpusReader"]:
        raise NotImplementedError("Subclasses must implement this method.")

    @abstractmethod
    def __iter__(self) -> Iterator[DocumentBatch]:
        """
        Return an iterator that yields files.

        Yields:
            Path: Each file found
        """
        pass

    @abstractmethod
    def make_doc(self, source: Any) -> Document:
        """
        Create a Document object from the given source.

        Args:
            source: The source from which to create the Document

        Returns:
            Document: The created Document object
        """
        raise NotImplementedError()
