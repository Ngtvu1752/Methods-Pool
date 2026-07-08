from readers.base import BaseReader
from errors import UnsupportedDatasetFormatError

_REGISTRY: dict[str, BaseReader] = {}

def register_reader(*formats: str):
    """ Decorator to register a reader class for specific dataset formats."""
    def decorator(cls: type[BaseReader]) -> type[BaseReader]:
        instance = cls()
        for fmt in formats: 
            key = fmt.lower().lstrip(".")
            if key in _REGISTRY:
                raise ValueError(f"Reader for format '{key}' is already registered by { _REGISTRY[key].__class__.__name__ }")
            _REGISTRY[key] = instance

        cls.supported_formats = set(formats)
        return cls
    return decorator


class ReaderRegistry:
    """Facade duy nhất mà hub.py cần biết — không cần import bất kỳ reader cụ thể nào."""

    @staticmethod
    def get(fmt: str) -> BaseReader:
        """Get the reader instance for the given dataset format."""
        key = fmt.lower().lstrip(".")
        reader = _REGISTRY.get(key)
        if reader is None:
            raise UnsupportedDatasetFormatError(fmt)
        return reader() if isinstance(reader, type) else reader
    
    @staticmethod
    def all_formats() -> list[str]:
        """Return a set of all supported dataset formats."""
        return sorted(_REGISTRY.keys())