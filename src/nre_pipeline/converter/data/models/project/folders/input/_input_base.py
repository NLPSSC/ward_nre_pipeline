from pathlib import Path

from nre_pipeline.converter.data.models.root_folders._folders_base import DataFolderRoot


class InputBase(DataFolderRoot):

    def __init__(self, *args, **kwargs) -> None:
        from nre_pipeline.common.env_vars._env_values_manager import EnvValues
        super().__init__(root_path = EnvValues.get_input_root(), *args, **kwargs)

    
