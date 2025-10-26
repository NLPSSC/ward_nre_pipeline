from pathlib import Path
from nre_pipeline.common.env_vars._env_values_manager import EnvValues
from nre_pipeline.converter.data.models.root_folders._folders_base import DataFolderRoot


class InputBase(DataFolderRoot):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    @property
    def root_folder(self) -> Path:
        return EnvValues.get_input_root()
