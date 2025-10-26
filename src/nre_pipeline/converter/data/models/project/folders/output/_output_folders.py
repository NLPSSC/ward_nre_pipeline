from pathlib import Path

from numpy import test

from nre_pipeline.common.env_vars._env_values_manager import EnvValues
from nre_pipeline.converter.data.models.root_folders._folders_base import DataFolderRoot


class OutputBase(DataFolderRoot):

    def __init__(self, *args, **kwargs) -> None:
        from nre_pipeline.common.env_vars._env_values_manager import EnvValues
        super().__init__(root_path=EnvValues.get_output_root(), *args, **kwargs)

    
