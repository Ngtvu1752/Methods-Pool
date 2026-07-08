from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class DatasetMetadata:
    """Catalog metadata for one approved data lake file."""

    id: str
    name: str
    path: Path
    file_format: str
    modality: str
    processing_domain: str
    size_bytes: int
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class DatasetPreview:
    """Generic preview response model kept for compatibility."""

    dataset_id: str
    rows: list[dict[str, Any]]
    columns: list[str]
    row_count: int
    limit: int
