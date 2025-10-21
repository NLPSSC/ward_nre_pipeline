from abc import ABC, abstractmethod
from threading import Thread

from loguru import logger


class ThreadLoopMixin(ABC):

    def __init__(self, *args, **kwargs) -> None:
        logger.debug(
            "Initializing ThreadLoopMixin, called by {}", self.__class__.__name__
        )
        super().__init__(*args, **kwargs)
        self._thread = Thread(target=self._thread_worker)
        # self.start()

    @abstractmethod
    def _thread_worker(self):
        raise NotImplementedError("Subclasses must implement this method.")

    def start(self):
        self._thread.start()

    def join(self):
        self._thread.join()
