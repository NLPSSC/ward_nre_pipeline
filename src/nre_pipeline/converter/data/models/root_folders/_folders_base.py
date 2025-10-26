from abc import ABC
from pathlib import Path
from nre_pipeline.converter.data.models.mixins._project_folder_mixin import (
    ProjectFolderMixin,
)
from nre_pipeline.converter.data.models.mixins._root_path_mixin import RootPathMixin


class DataFolderRoot(ABC, ProjectFolderMixin, RootPathMixin):
    def __init__(self, root_path: Path, *args, **kwargs) -> None:
        super().__init__(root_path=root_path, *args, **kwargs)

    @property
    def project_name(self) -> str:
        from .....common.env_vars._env_values_manager import EnvValues

        _project_name: str = EnvValues.get_project_name()
        return _project_name

    @property
    def root_path(self) -> Path:
        return self._root_path

    def __str__(self) -> str:
        return str(self.root_path)
