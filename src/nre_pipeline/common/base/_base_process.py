from abc import ABC, abstractmethod
from multiprocessing import Process


class _BaseProcess(ABC, Process):

    def __init__(self) -> None:
        super().__init__(name=self.get_process_name())

    def run(self) -> None:
        print(f"Process {self.name} started with PID: {self.pid}")
        self._runner()
        print(f"Process {self.name} finished.")

    @abstractmethod
    def get_process_name(self) -> str:
        raise NotImplementedError("Must implement the process_name property")

    @abstractmethod
    def _runner(self) -> None:
        raise NotImplementedError("Must implement the _runner method")
