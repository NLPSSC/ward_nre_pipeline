from abc import abstractmethod
from pathlib import Path


class ProjectFolderMixin:

    @property
    @abstractmethod
    def project_name(self) -> str:
        raise NotImplementedError("Must implement project_name")

    @property
    @abstractmethod
    def root_path(self) -> Path:
        raise NotImplementedError("Must implement root_path")
