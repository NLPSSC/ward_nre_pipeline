from abc import ABC


class PipelineComponent(ABC):
    def __init__(self, *args, **kwargs):
        lock_folder = kwargs.pop("lock_folder", None)
        if lock_folder is None:
            raise ValueError("lock_folder must be provided")
        
        start here how to make dependencies

        super().__init__(*args, **kwargs)

    def get_component_name(self) -> str:
        return self.__class__.__name__
