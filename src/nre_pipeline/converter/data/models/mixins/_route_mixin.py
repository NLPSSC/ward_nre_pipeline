from abc import ABC, abstractmethod
from pathlib import Path


from ._root_path_mixin import RootPathMixin


class RouteMixin(ABC, RootPathMixin):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    @property
    def root_path(self) -> Path:
        return super().root_path / self._route_segment

    @property
    @abstractmethod
    def _route_segment(self) -> str:
        raise NotImplementedError("Must implement _route_segment method")
