from abc import ABC, abstractmethod
from typing import Optional

from nre_pipeline.converter.data.models.mixins._route_mixin import RouteMixin
from nre_pipeline.converter.data.models.project.folders.input._input_base import (
    InputBase,
)
from nre_pipeline.converter.data.models.routes._nonexitent_route_exception import (
    NonExistentRouteSegmentException,
)


class CorpusRoute(InputBase, RouteMixin):

    _corpus_route_names = set()

    def __init__(self, name: str, corpus_route: Optional[str], *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        if len(name) < 1:
            raise ValueError(
                f'Corpus route name must be at least one character long (invalid name "{name}")'
            )

        if name in CorpusRoute._corpus_route_names:
            raise ValueError(
                f'Corpus route name must be unique (duplicate name "{name}")'
            )

        # Add corpus name
        self._name: str = name
        CorpusRoute._corpus_route_names.add(name)

        # Add corpus route
        self._corpus_route: Optional[str] = corpus_route

    @property
    def _route_segment(self) -> str:
        if self._corpus_route is None:
            raise NonExistentRouteSegmentException(self._name)
        return self._corpus_route

    def _validate_route(self):
        if self.root_path is None:
            raise RuntimeError("Route cannot be None")
        if self.root_path.exists() is False:
            raise RuntimeError(f"Route does not exist: {self.root_path}")

    @property
    def name(self) -> str:
        return self._name
