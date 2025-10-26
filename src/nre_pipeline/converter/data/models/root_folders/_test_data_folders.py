# from pathlib import Path

# from .....common.env_vars._env_values_manager import EnvValues
# from ._input_folders import FoldersBase


# class TestData(FoldersBase):
#     def __init__(self, *args, **kwargs) -> None:
#         super().__init__(*args, **kwargs)
#         self._test_data_path: Path = EnvValues.get_test_data_path()

#     @property
#     def root_path(self) -> Path:
#         return self._test_data_path
