class LockFolderMixin:
    def __init__(self, lock_folder: str, *args, **kwargs):
        self._lock_folder = lock_folder
        super().__init__(*args, **kwargs)