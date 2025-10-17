import json
import sqlite3
import tempfile
from typing import List

from nre_pipeline.models._nlp_result import NLPResult, NLPResultItem
from nre_pipeline.writer.database._sqlite import SQLiteNLPWriter


def mock_results(n):
    def make_value(row, col):
        if col % 2 == 0:
            return {"value": f"value_{row}_{col}", "value_type": str}
        return {"value": col * row, "value_type": int}

    for row_idx in range(n):
        results = [
            NLPResultItem(key=f"key_{col_idx}", **make_value(row_idx, col_idx))
            for col_idx in range(3)
        ]
        yield NLPResult(note_id=row_idx + 1, results=results)


if __name__ == "__main__":
    # Use a temporary directory instead of NamedTemporaryFile
    import os
    import tempfile

    test_values: List[NLPResult] = list(mock_results(10))
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = os.path.join(temp_dir, "test.db")
        writer = SQLiteNLPWriter(db_path=db_path)
        for result in test_values:
            writer.record(result)

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {writer.table_name}")
        rows = cursor.fetchall()
        conn.close()

        read_values = [r[1:] for r in rows]
        flattened_test_values = [
            (t.note_id, *[x.value for x in t.results]) for t in test_values
        ]

        assert read_values == flattened_test_values
