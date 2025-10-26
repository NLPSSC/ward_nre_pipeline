from typing import Generic, TypeVar
from nre_pipeline.converter.data.models.mixins._route_mixin import RouteMixin
from nre_pipeline.converter.data.models.project_folders.output.results._route_results_folder import ResultsFolderRoute


TOutputType = TypeVar("TOutputType")


class OutputRoute(Generic[TOutputType], ResultsFolderRoute, RouteMixin):
    def __init__(self) -> None:
        super().__init__()

    @property
    def _route_segment(self) -> str:
        return "output"
