from nre_pipeline.converter.data.models.root_folders._test_data_folders import TestData
from nre_pipeline.converter.data.models.mixins._route_mixin import RouteMixin


class CorpusRoute(TestData, RouteMixin):
    def __init__(self, route: str) -> None:
        super().__init__()
        self._route = route

    @property
    def route_segment(self) -> str:
        return self._route
