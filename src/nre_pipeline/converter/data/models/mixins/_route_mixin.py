from abc import ABC, abstractmethod
from pathlib import Path


from ._root_path_mixin import RootPathMixin


class RouteMixin(ABC, RootPathMixin):
    @property
    def route(self) -> Path:
        return self.root_path / self.route_segment

    @property
    @abstractmethod
    def route_segment(self) -> str:
        raise NotImplementedError("Must implement route_segment method")
