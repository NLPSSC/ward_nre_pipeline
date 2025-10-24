from typing import Literal, TypeAlias
TQueueEmpty: TypeAlias = Literal["QUEUE_EMPTY","PROCESSING_COMPLETED"]
TProcessingStatus: TypeAlias = Literal["complete", "failure", "processing", "not_started"]

QUEUE_EMPTY: TQueueEmpty = "QUEUE_EMPTY"
PROCESSING_COMPLETED: TQueueEmpty = "PROCESSING_COMPLETED"