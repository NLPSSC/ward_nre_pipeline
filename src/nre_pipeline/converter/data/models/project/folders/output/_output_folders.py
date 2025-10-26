from pathlib import Path

from numpy import test

from nre_pipeline.common.env_vars._env_values_manager import EnvValues
from nre_pipeline.converter.data.models.root_folders._folders_base import DataFolderRoot


class OutputBase(DataFolderRoot):

    def __init__(self) -> None:
        pass

    @property
    def root_folder(self) -> Path:
        return EnvValues.get_output_root()



# vals = [
# f"_env_key=={_env_key}",
# f"_validation_method=={_validation_method}",
# f"_expected=={_expected}\n",
# f"_expect_to_succeed=={_expect_to_succeed}\n"
# ]
# test_cond = " and ".join(vals)
# print(test_cond)