import csv
from statistics import median
from typing import Any

from actions.base import ActionParam, BaseAction
from actions.registry import register_action
from models import StructuredDataset


COLUMN_PARAM = ActionParam(
    name="column",
    type=str,
    description="Name of the numeric column to analyze.",
)


class StructuredNumericColumnAction(BaseAction):
    """Shared helpers for numeric-column actions on structured datasets."""

    supported_dataset_types = (StructuredDataset,)

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

    def _scan_numeric_column(
        self,
        dataset: StructuredDataset,
        column: str,
        collect_values: bool = False,
    ) -> dict[str, Any]:
        if dataset.source_format != "csv":
            raise ValueError(
                "Structured numeric column actions currently support CSV-backed "
                "structured datasets only."
            )

        stats = {
            "min": None,
            "max": None,
            "sum": 0.0,
            "numeric_count": 0,
            "missing_count": 0,
            "invalid_count": 0,
            "rows_scanned": 0,
            "values": [] if collect_values else None,
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

                if collect_values:
                    stats["values"].append(value)

        return stats

    def _base_response(
        self,
        dataset: StructuredDataset,
        column: str,
        stats: dict[str, Any],
    ) -> dict[str, Any]:
        return {
            "dataset_id": dataset.dataset_id,
            "file_format": dataset.source_format,
            "column": column,
            "numeric_count": stats["numeric_count"],
            "missing_count": stats["missing_count"],
            "invalid_count": stats["invalid_count"],
            "rows_scanned": stats["rows_scanned"],
        }

    def _average(self, stats: dict[str, Any]) -> float | None:
        if stats["numeric_count"] == 0:
            return None

        return stats["sum"] / stats["numeric_count"]

    def _percentile(self, values: list[float], percentile: float) -> float | None:
        if not values:
            return None

        sorted_values = sorted(values)
        rank = (percentile / 100) * (len(sorted_values) - 1)
        lower_index = int(rank)
        upper_index = min(lower_index + 1, len(sorted_values) - 1)
        weight = rank - lower_index

        return (
            sorted_values[lower_index] * (1 - weight)
            + sorted_values[upper_index] * weight
        )

    def _get_percentile(self, kwargs: dict[str, Any]) -> float:
        try:
            percentile = float(kwargs.get("percentile", 50))
        except (TypeError, ValueError):
            raise ValueError("percentile must be a number between 0 and 100.")

        if percentile < 0 or percentile > 100:
            raise ValueError("percentile must be between 0 and 100.")

        return percentile

    def _detect_dialect(self, sample: str) -> type[csv.Dialect] | csv.Dialect:
        try:
            return csv.Sniffer().sniff(sample)
        except csv.Error:
            return csv.excel


@register_action
class StructuredColumnMinAction(StructuredNumericColumnAction):
    name = "structured_column_min"
    description = "Calculate the minimum value of one numeric column in a structured dataset."
    params = (COLUMN_PARAM,)

    def execute(self, dataset: StructuredDataset, **kwargs: Any) -> dict[str, Any]:
        column = self._get_column(dataset, kwargs)
        stats = self._scan_numeric_column(dataset, column)
        return self._base_response(dataset, column, stats) | {"min": stats["min"]}


@register_action
class StructuredColumnMaxAction(StructuredNumericColumnAction):
    name = "structured_column_max"
    description = "Calculate the maximum value of one numeric column in a structured dataset."
    params = (COLUMN_PARAM,)

    def execute(self, dataset: StructuredDataset, **kwargs: Any) -> dict[str, Any]:
        column = self._get_column(dataset, kwargs)
        stats = self._scan_numeric_column(dataset, column)
        return self._base_response(dataset, column, stats) | {"max": stats["max"]}


@register_action
class StructuredColumnSumAction(StructuredNumericColumnAction):
    name = "structured_column_sum"
    description = "Calculate the sum of one numeric column in a structured dataset."
    params = (COLUMN_PARAM,)

    def execute(self, dataset: StructuredDataset, **kwargs: Any) -> dict[str, Any]:
        column = self._get_column(dataset, kwargs)
        stats = self._scan_numeric_column(dataset, column)
        return self._base_response(dataset, column, stats) | {"sum": stats["sum"]}


@register_action
class StructuredColumnAverageAction(StructuredNumericColumnAction):
    name = "structured_column_average"
    description = "Calculate the average value of one numeric column in a structured dataset."
    params = (COLUMN_PARAM,)

    def execute(self, dataset: StructuredDataset, **kwargs: Any) -> dict[str, Any]:
        column = self._get_column(dataset, kwargs)
        stats = self._scan_numeric_column(dataset, column)
        return self._base_response(dataset, column, stats) | {
            "average": self._average(stats)
        }


@register_action
class StructuredColumnMedianAction(StructuredNumericColumnAction):
    name = "structured_column_median"
    description = "Calculate the median value of one numeric column in a structured dataset."
    params = (COLUMN_PARAM,)

    def execute(self, dataset: StructuredDataset, **kwargs: Any) -> dict[str, Any]:
        column = self._get_column(dataset, kwargs)
        stats = self._scan_numeric_column(dataset, column, collect_values=True)
        values = stats["values"]
        return self._base_response(dataset, column, stats) | {
            "median": median(values) if values else None
        }


@register_action
class StructuredColumnPercentileAction(StructuredNumericColumnAction):
    name = "structured_column_percentile"
    description = "Calculate a percentile for one numeric column in a structured dataset."
    params = (
        COLUMN_PARAM,
        ActionParam(
            name="percentile",
            type=float,
            default=50.0,
            description="Percentile to calculate, from 0 to 100.",
        ),
    )

    def execute(self, dataset: StructuredDataset, **kwargs: Any) -> dict[str, Any]:
        column = self._get_column(dataset, kwargs)
        percentile = self._get_percentile(kwargs)
        stats = self._scan_numeric_column(dataset, column, collect_values=True)
        return self._base_response(dataset, column, stats) | {
            "percentile": percentile,
            "value": self._percentile(stats["values"], percentile),
        }


@register_action
class StructuredColumnProfileAction(StructuredNumericColumnAction):
    name = "structured_column_profile"
    description = "Return a numeric profile for one column in a structured dataset."
    params = (COLUMN_PARAM,)

    def execute(self, dataset: StructuredDataset, **kwargs: Any) -> dict[str, Any]:
        column = self._get_column(dataset, kwargs)
        stats = self._scan_numeric_column(dataset, column, collect_values=True)
        values = stats["values"]

        return self._base_response(dataset, column, stats) | {
            "min": stats["min"],
            "max": stats["max"],
            "sum": stats["sum"],
            "average": self._average(stats),
            "median": median(values) if values else None,
            "p25": self._percentile(values, 25),
            "p75": self._percentile(values, 75),
        }
