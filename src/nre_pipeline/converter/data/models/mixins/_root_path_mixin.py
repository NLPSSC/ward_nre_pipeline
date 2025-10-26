from abc import abstractmethod
from pathlib import Path


class RootPathMixin:

    def __init__(self, root_path: Path, *args, **kwargs) -> None:
        self._root_path: Path = root_path
        super().__init__(*args, **kwargs)

    @property
    @abstractmethod
    def root_path(self) -> Path:
        raise NotImplementedError("Must implement root_path property")
