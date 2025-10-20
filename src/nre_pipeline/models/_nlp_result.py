from loguru import logger
from dataclasses import dataclass
from typing import Any, List

from nre_pipeline.models._nlp_result_item import NLPResultFeature


@dataclass
class NLPResultFeatures:
    note_id: str | int
    result_features: List[NLPResultFeature]

    def to_dict(self) -> dict[str, Any]:
        """
        Convert features list to a dict mapping keys to values.
        If a key appears multiple times, aggregate values into a list (preserving order).
        """
        result: dict[str, Any] = {}
        for feature in self.result_features:
            if feature.key in result:
                existing = result[feature.key]
                if isinstance(existing, list):
                    existing.append(feature.value)
                else:
                    result[feature.key] = [existing, feature.value]
                logger.warning(
                    f"Duplicate feature key '{feature.key}' encountered; aggregated into list."
                )
            else:
                result[feature.key] = feature.value
        return result

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, NLPResultFeatures):
            return False
        note_id_eq: bool = self.note_id == value.note_id
        if note_id_eq is False:
            logger.warning(f"Note IDs do not match: {self.note_id} != {value.note_id}")
            return False

        results_eq = self.result_features == value.result_features
        if results_eq is False:
            logger.warning(
                f"Results do not match: {self.result_features} != {value.result_features}"
            )
            return False

        return note_id_eq and results_eq

    def __repr__(self):
        [r for r in self.result_features]
        return f"""
Note ID: {self.note_id}
Results: {self.result_features}
"""
