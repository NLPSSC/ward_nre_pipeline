import os
from typing import Any, Dict, List, Union, cast
from nre_pipeline.common.base._base_writer import NLPResultWriter
from nre_pipeline.models._nlp_result import NLPResultItem


DEFAULT_DELIMITER = "|"


# /results{id}.db
class CSVWriter(NLPResultWriter):

    def __init__(
        self,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        if os.path.exists(self.output_path):
            raise FileExistsError(f"File {self.output_path} already exists.")
        self._output_fh = open(self.output_path, "w")
        self._header_written = False

    def _record(self, nlp_result: Union[NLPResultItem, List[NLPResultItem]]) -> None:
        """Record one or more NLP result items in the CSV file.

        Args:
            nlp_result (Union[NLPResultItem, List[NLPResultItem]]): NLP result item or list of items to record.
        """
        if isinstance(nlp_result, List) is False:
            nlp_result = [cast(NLPResultItem, nlp_result)]
        for item in cast(List[NLPResultItem], nlp_result):
            if not self._header_written:
                headers: List[str] = list(item.to_dict().keys())
                headers.insert(0, "note_id")
                self._output_fh.write(DEFAULT_DELIMITER.join(headers) + "\n")
                self._header_written = True
            values: List[str] = [str(value) for value in item.to_dict().values()]
            values.insert(0, str(item.note_id))
            row_val: str = DEFAULT_DELIMITER.join(
                [v.replace(DEFAULT_DELIMITER, rf"\{DEFAULT_DELIMITER}") for v in values]
            )
            self._output_fh.write(row_val + "\n")

    def writer_details(self) -> Dict[str, Any]:
        return {"csv_path": self.output_path}

    def _build_output_file_name(self) -> str:
        return f"results_{self._get_results_id()}.csv"

    def _on_write_complete(self) -> None:
        self._output_fh.close()
        with open(f"{self.output_path}.notes.md", "w") as notes_fh:
            notes_fh.write("# Notes\n")
            notes_fh.write("\n")
            notes_fh.write(f"Delimiter Used: {DEFAULT_DELIMITER}\n")
