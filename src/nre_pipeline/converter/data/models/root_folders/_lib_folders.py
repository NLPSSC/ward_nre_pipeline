# from abc import ABC
# from pathlib import Path

# from .....common.env_vars._env_values_manager import EnvValues
# from ._folders_base import FoldersBase


# class LibFoldersBase(FoldersBase):

#     def __init__(self) -> None:
#         super().__init__()


# class QuickUMLSPath(LibFoldersBase):

#     def __init__(self) -> None:
#         super().__init__()
#         self._quickumls_path = EnvValues.get_quickumls_path()
#         self._dev_umls_key_path = EnvValues.get_dev_umls_key_path()

#     @property
#     def quickumls_path(self) -> Path:
#         return self._quickumls_path

#     @property
#     def dev_umls_key_path(self) -> Path:
#         return self._dev_umls_key_path
