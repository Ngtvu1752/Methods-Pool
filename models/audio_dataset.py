from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from models.dataset_metadata import DatasetMetadata


@dataclass(frozen=True)
class AudioDataset:
    """Normalized object for audio datasets."""

    metadata: DatasetMetadata
    path: Path
    waveform: Any | None = None
    duration_seconds: float | None = None
    sample_rate: int | None = None
    channels: int | None = None
    source_format: str | None = None
    extra: dict[str, Any] = field(default_factory=dict)

    @property
    def dataset_id(self) -> str:
        return self.metadata.id
