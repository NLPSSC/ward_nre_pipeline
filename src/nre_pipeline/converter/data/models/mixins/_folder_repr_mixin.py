from ._project_folder_mixin import ProjectFolderMixin


class FolderReprMixin(ProjectFolderMixin):

    def __repr__(self) -> str:
        cls_name: str = self.__class__.__name__
        return f"<{cls_name} project_name={self.project_name}> {self.root_path}"
