from abc import abstractmethod
from pathlib import Path


class RootPathMixin:

    @property
    @abstractmethod
    def root_path(self) -> Path:
        raise NotImplementedError("Must implement root_path property")
