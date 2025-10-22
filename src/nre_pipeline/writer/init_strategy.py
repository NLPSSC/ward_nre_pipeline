from abc import abstractmethod
from nre_pipeline.writer.mixins.management import WriterManagementMixin


class _InitStrategy:

    @abstractmethod
    def __call__(self, writer: WriterManagementMixin):
        pass


class ResetEachUseStrategy(_InitStrategy):

    def __call__(self, writer: WriterManagementMixin):
        ####################################################################
        # 1) Get the path to the path to the current .db file
        # 2) Close any existing connections
        # 3) Delete .db file and any related files
        # 4) Recreate the database
        ####################################################################

        writer._close()
        writer._delete()
        writer._create()
