from abc import ABC, abstractmethod
from multiprocessing import Process
import threading
from loguru import logger


class _BaseProcess(ABC, Process):

    def __init__(self) -> None:
        threading.current_thread().name = self.get_process_name()
        super().__init__(name=self.get_process_name())

    @classmethod
    @abstractmethod
    def create(cls, manager, **config):
        raise NotImplementedError("Must implement the create method")

    def run(self) -> None:
        logger.debug(f"Process {self.name} started with PID: {self.pid}")
        self._runner()
        logger.debug(f"Process {self.name} finished.")

    @abstractmethod
    def get_process_name(self) -> str:
        raise NotImplementedError("Must implement the process_name property")

    @abstractmethod
    def _runner(self) -> None:
        raise NotImplementedError("Must implement the _runner method")
