import csv

from itertools import islice
from typing import Any
from pathlib import Path

from models import DatasetMetadata, StructuredDataset
from readers.base import BaseReader
from readers.registry import register_reader

@register_reader("csv")
class CsvReader(BaseReader):
    """Inspect CSV files without loading the whole file into memory."""
    default_sample_size = 50

    def read(
        self,
        dataset: DatasetMetadata,
    ) -> StructuredDataset:
        sample_rows, columns, dialect_name = self._inspect_csv(
            dataset=dataset,
            sample_size=self.default_sample_size,
        )

        return StructuredDataset(
            metadata=dataset,
            source_path=dataset.path,
            columns=columns,
            sample_rows=sample_rows,
            row_count=None,
            source_format=dataset.file_format,
            extra={
                "dialect": dialect_name,
                "sample_size": len(sample_rows),
                "row_count_is_known": False,
                "supports_chunked_read": True,
                "supports_projection": True,
                "recommended_actions": [
                    "preview",
                    "schema_inference",
                    "aggregate",
                    "filter",
                    "query",
                ],
            },
        )

    def _inspect_csv(
        self,
        dataset: DatasetMetadata,
        sample_size: int,
    ) -> tuple[list[dict[str, Any]], list[str], str]:
        with dataset.path.open("r", encoding="utf-8-sig", errors="replace", newline="") as file:
            sample = file.read(4096)
            file.seek(0)
            dialect = self._detect_dialect(sample)
            reader = csv.DictReader(file, dialect=dialect)
            rows = [dict(row) for row in islice(reader, sample_size)]
            columns = list(reader.fieldnames or [])

        return rows, columns, self._dialect_name(dialect)

    def _detect_dialect(self, sample: str) -> type[csv.Dialect] | csv.Dialect:
        try:
            return csv.Sniffer().sniff(sample)
        except csv.Error:
            return csv.excel

    def _dialect_name(self, dialect: type[csv.Dialect] | csv.Dialect) -> str:
        return getattr(dialect, "__name__", dialect.__class__.__name__)
