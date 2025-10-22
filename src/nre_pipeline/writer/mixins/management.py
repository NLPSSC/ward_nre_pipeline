class WriterManagementMixin:

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def reset(self):
        self._close()
        self._delete()
        self._create()

    def _close(self): ...

    def _delete(self): ...

    def _create(self): ...
