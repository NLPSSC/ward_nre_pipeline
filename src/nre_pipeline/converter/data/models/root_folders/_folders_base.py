from abc import ABC, abstractmethod

from nre_pipeline.converter.data.models.mixins._project_folder_mixin import ProjectFolderMixin
from nre_pipeline.converter.data.models.mixins._root_path_mixin import RootPathMixin

from .....common.env_vars._env_values_manager import EnvValues


class FoldersBase(ABC, ProjectFolderMixin, RootPathMixin):
    def __init__(self) -> None:
        self._project_name: str = EnvValues.get_project_name()
        super().__init__()

    @property
    def project_name(self) -> str:
        return self._project_name

    @abstractmethod
    def __str__(self) -> str:
        return str(self.root_path)
