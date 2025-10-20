from typing import TypeAlias
from typing_extensions import Literal

from nre_pipeline.models._nlp_result import NLPResult

TQueueEmpty: TypeAlias = Literal["QUEUE_EMPTY"]


TQueueItem: TypeAlias = NLPResult | TQueueEmpty
