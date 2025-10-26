from abc import ABC
from nre_pipeline.converter.data.models.mixins._project_folder_mixin import (
    ProjectFolderMixin,
)
from nre_pipeline.converter.data.models.mixins._root_path_mixin import RootPathMixin
from .....common.env_vars._env_values_manager import EnvValues

__project_name: str = EnvValues.get_project_name()


class DataFolderRoot(ABC, ProjectFolderMixin, RootPathMixin):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    @property
    def project_name(self) -> str:
        return __project_name

    def __str__(self) -> str:
        return str(self.root_path)
