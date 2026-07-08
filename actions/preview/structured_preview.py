from typing import Any

from actions.base import BaseAction
from actions.registry import register_action
from models import StructuredDataset


@register_action
class StructuredPreviewAction(BaseAction):
    name = "preview"
    supported_dataset_types = (StructuredDataset,)

    def execute(
        self,
        dataset: StructuredDataset,
        **kwargs: Any,
    ) -> dict[str, Any]:
        limit = self._get_limit(kwargs)
        rows = dataset.sample_rows[:limit]

        return {
            "dataset_id": dataset.dataset_id,
            "file_format": dataset.source_format,
            "preview_type": "table",
            "columns": dataset.columns,
            "rows": rows,
            "row_count_returned": len(rows),
            "row_count_known": dataset.row_count is not None,
            "row_count": dataset.row_count,
            "limit": limit,
            "source_is_lazy": True,
        }

    def _get_limit(self, kwargs: dict[str, Any]) -> int:
        try:
            limit = int(kwargs.get("limit", 20))
        except (TypeError, ValueError):
            raise ValueError("limit must be an integer.")

        return max(1, min(limit, 100))
