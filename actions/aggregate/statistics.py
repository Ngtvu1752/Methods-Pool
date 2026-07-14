import csv
from typing import Any

from actions.base import ActionParam, BaseAction
from actions.registry import register_action
from models import StructuredDataset


@register_action
class StructuredColumnStatisticsAction(BaseAction):
    name = "column_statistics"
    description = "Calculate min, max, and mean for one numeric column in a structured dataset."
    params = (
        ActionParam(
            name="column",
            type=str,
            description="Name of the numeric column to analyze.",
        ),
    )
    supported_dataset_types = (StructuredDataset,)

    def execute(
        self,
        dataset: StructuredDataset,
        **kwargs: Any,
    ) -> dict[str, Any]:
        column = self._get_column(dataset, kwargs)

        if dataset.source_format != "csv":
            raise ValueError(
                "column_statistics currently supports CSV-backed structured datasets only."
            )

        stats = self._scan_csv_column(dataset, column)
        mean = (
            stats["sum"] / stats["numeric_count"]
            if stats["numeric_count"] > 0
            else None
        )

        return {
            "dataset_id": dataset.dataset_id,
            "file_format": dataset.source_format,
            "column": column,
            "min": stats["min"],
            "max": stats["max"],
            "mean": mean,
            "numeric_count": stats["numeric_count"],
            "missing_count": stats["missing_count"],
            "invalid_count": stats["invalid_count"],
            "rows_scanned": stats["rows_scanned"],
        }

    def _get_column(
        self,
        dataset: StructuredDataset,
        kwargs: dict[str, Any],
    ) -> str:
        column = kwargs.get("column")

        if not isinstance(column, str) or not column.strip():
            raise ValueError("column must be a non-empty string.")

        column = column.strip()
        if column not in dataset.columns:
            raise ValueError(
                f"Column '{column}' not found. Available columns: {dataset.columns}"
            )

        return column

    def _scan_csv_column(
        self,
        dataset: StructuredDataset,
        column: str,
    ) -> dict[str, Any]:
        stats = {
            "min": None,
            "max": None,
            "sum": 0.0,
            "numeric_count": 0,
            "missing_count": 0,
            "invalid_count": 0,
            "rows_scanned": 0,
        }

        with dataset.source_path.open(
            "r",
            encoding="utf-8-sig",
            errors="replace",
            newline="",
        ) as file:
            sample = file.read(4096)
            file.seek(0)
            dialect = self._detect_dialect(sample)
            reader = csv.DictReader(file, dialect=dialect)

            for row in reader:
                stats["rows_scanned"] += 1
                raw_value = row.get(column)

                if raw_value is None or str(raw_value).strip() == "":
                    stats["missing_count"] += 1
                    continue

                try:
                    value = float(str(raw_value).strip())
                except ValueError:
                    stats["invalid_count"] += 1
                    continue

                stats["sum"] += value
                stats["numeric_count"] += 1
                stats["min"] = value if stats["min"] is None else min(stats["min"], value)
                stats["max"] = value if stats["max"] is None else max(stats["max"], value)

        return stats

    def _detect_dialect(self, sample: str) -> type[csv.Dialect] | csv.Dialect:
        try:
            return csv.Sniffer().sniff(sample)
        except csv.Error:
            return csv.excel
