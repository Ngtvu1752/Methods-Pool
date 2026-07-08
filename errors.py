class DataLakeError(Exception):
    """Base error for data lake operations."""


class DatasetNotFoundError(DataLakeError):
    def __init__(self, dataset_id: str):
        super().__init__(f"Dataset not found: {dataset_id}")
        self.dataset_id = dataset_id


class UnsupportedDatasetFormatError(DataLakeError):
    def __init__(self, file_format: str):
        super().__init__(f"Unsupported dataset format: {file_format}")
        self.file_format = file_format


class UnsafePathError(DataLakeError):
    def __init__(self, path: str):
        super().__init__(f"Path is outside the configured data lake root: {path}")


class UnsafeQueryError(DataLakeError):
    def __init__(self, reason: str):
        super().__init__(f"Unsafe query: {reason}")