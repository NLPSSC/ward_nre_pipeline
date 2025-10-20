from nre_pipeline.models._nlp_result_item import NLPResultItem
from loguru import logger
from dataclasses import dataclass
from typing import List


@dataclass
class NLPResult:
    note_id: str | int
    results: List[NLPResultItem]

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, NLPResult):
            return False
        note_id_eq: bool = self.note_id == value.note_id
        if note_id_eq is False:
            logger.warning(f"Note IDs do not match: {self.note_id} != {value.note_id}")
            return False

        results_eq = self.results == value.results
        if results_eq is False:
            logger.warning(f"Results do not match: {self.results} != {value.results}")
            return False

        return note_id_eq and results_eq

    def __repr__(self):
        [r for r in self.results]
        return f"""
Note ID: {self.note_id}
Results: {self.results}
"""
