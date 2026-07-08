from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from models.dataset_metadata import DatasetMetadata


@dataclass(frozen=True)
class VideoDataset:
    """Normalized object for video datasets."""

    metadata: DatasetMetadata
    path: Path
    video: Any | None = None
    duration_seconds: float | None = None
    width: int | None = None
    height: int | None = None
    frame_rate: float | None = None
    source_format: str | None = None
    extra: dict[str, Any] = field(default_factory=dict)

    @property
    def dataset_id(self) -> str:
        return self.metadata.id
