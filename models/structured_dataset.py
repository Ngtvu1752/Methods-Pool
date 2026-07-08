from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from models.dataset_metadata import DatasetMetadata


@dataclass(frozen=True)
class StructuredDataset:
    """Normalized object for tabular or table-like datasets."""

    metadata: DatasetMetadata
    source_path: Path
    columns: list[str]
    row_count: int | None = None
    source_format: str | None = None
    sample_rows: list[dict[str, Any]] = field(default_factory=list)
    extra: dict[str, Any] = field(default_factory=dict)

    @property
    def dataset_id(self) -> str:
        return self.metadata.id
