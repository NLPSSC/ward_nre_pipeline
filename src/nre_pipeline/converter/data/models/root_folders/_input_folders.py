from pathlib import Path


from .....common.env_vars._env_values_manager import EnvValues
from ._folders_base import FoldersBase


class InputSourceFolder(FoldersBase):

    def __init__(self) -> None:
        self._input_root: Path = EnvValues.get_input_root_path()
        super().__init__()

    @property
    def root_folder(self) -> Path:
        return self._input_root

    @property
    def route_segment(self) -> str:
        return ""

    def __str__(self) -> str:
        return str(self._input_root)
