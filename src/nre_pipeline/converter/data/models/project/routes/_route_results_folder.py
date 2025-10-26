from nre_pipeline.converter.data.models.mixins._route_mixin import RouteMixin
from nre_pipeline.converter.data.models.project.folders.output._output_folders import OutputBase



class ResultsFolderRoute(OutputBase, RouteMixin):

    def __init__(self) -> None:
        super().__init__()

    @property
    def _route_segment(self) -> str:
        return "results"
