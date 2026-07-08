from typing import Any

from actions.base import BaseAction
from actions.registry import register_action
from models import StructuredDataset


@register_action
class StructuredSchemaAction(BaseAction):
    name = "schema"
    supported_dataset_types = (StructuredDataset,)

    def execute(
        self,
        dataset: StructuredDataset,
        **kwargs: Any,
    ) -> dict[str, Any]:
        return {
            "dataset_id": dataset.dataset_id,
            "file_format": dataset.source_format,
            "schema_available": True,
            "columns": [
                {
                    "name": column,
                    "inferred_type": self._infer_column_type(
                        [row.get(column, "") for row in dataset.sample_rows]
                    ),
                }
                for column in dataset.columns
            ],
            "inferred_from_sample_rows": len(dataset.sample_rows),
        }

    def _infer_column_type(self, values: list[Any]) -> str:
        non_empty = [
            str(value).strip()
            for value in values
            if value is not None and str(value).strip() != ""
        ]

        if not non_empty:
            return "unknown"

        if all(self._is_int(value) for value in non_empty):
            return "integer"

        if all(self._is_float(value) for value in non_empty):
            return "number"

        return "string"

    def _is_int(self, value: str) -> bool:
        try:
            int(value)
            return True
        except ValueError:
            return False

    def _is_float(self, value: str) -> bool:
        try:
            float(value)
            return True
        except ValueError:
            return False