from pathlib import Path
from .....common.env_vars._env_values_manager import EnvValues
from ..mixins._route_mixin import RouteMixin
from ._folders_base import FoldersBase


class OutputBase(FoldersBase):

    def __init__(self) -> None:
        pass

    @property
    def root_folder(self) -> Path:
        return EnvValues.get_output_root()


class ResultsFolder(OutputBase, RouteMixin):

    def __init__(self) -> None:
        super().__init__()

    @property
    def route_segment(self) -> str:
        return "results"


class SearchTreeRoute(ResultsFolder, RouteMixin):
    def __init__(self) -> None:
        super().__init__()

    @property
    def route_segment(self) -> str:
        return "search_tree"


class CSVResultsRoute(ResultsFolder, RouteMixin):

    def __init__(self) -> None:
        super().__init__()

    @property
    def route_segment(self) -> str:
        return "csv"


class SqliteResultsRoute(ResultsFolder, RouteMixin):

    def __init__(self) -> None:
        super().__init__()

    @property
    def route_segment(self) -> str:
        return "sqlite_db"
