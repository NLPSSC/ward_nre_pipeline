from abc import ABC, abstractmethod
from pathlib import Path


from ._root_path_mixin import RootPathMixin


class RouteMixin(ABC, RootPathMixin):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    @property
    def route_path(self) -> Path:
        _route: Path = self._root_path / "/".join([x for x in str(self._route_segment).split("/") if len(x) > 0])
        return _route

    @property
    @abstractmethod
    def _route_segment(self) -> str:
        raise NotImplementedError("Must implement _route_segment method")
    
    @property
    @abstractmethod
    def name(self):
        raise NotImplementedError("Must implement name property")
