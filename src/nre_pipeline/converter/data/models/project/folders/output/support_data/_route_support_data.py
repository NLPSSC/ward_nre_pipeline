from pathlib import Path

from ...mixins._route_mixin import RouteMixin
from ....routes._route_results_folder import ResultsFolderRoute
from ......common.env_vars._env_values_manager import EnvValues
from ...root_folders._folders_base import DataFolderRoot

class SupportDataRoute(ResultsFolderRoute, RouteMixin):
    def __init__(self) -> None:
        super().__init__()

    @property
    def _route_segment(self) -> str:
        return "support_data"