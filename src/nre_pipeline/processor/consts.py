from typing import TypeAlias
from typing_extensions import Literal

from nre_pipeline.models._nlp_result import NLPResultItem


TQueueItem: TypeAlias = NLPResultItem | TQueueEmpty
