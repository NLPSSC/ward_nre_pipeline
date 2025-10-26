from abc import ABC, abstractmethod
from nre_pipeline.converter.data.models.root_folders._test_data_folders import TestData
from nre_pipeline.converter.data.models.mixins._route_mixin import RouteMixin


class CorpusRoute(TestData, RouteMixin):
    def __init__(self, corpus_route: str, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.corpus_route = corpus_route
        self._validate_route()

    @property
    def _route_segment(self) -> str:
        return self.corpus_route

    def _validate_route(self):
        if self.root_path is None:
            raise RuntimeError("Route cannot be None")
        if self.root_path.exists() is False:
            raise RuntimeError(f"Route does not exist: {self.root_path}")
