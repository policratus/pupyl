"""Exceptions regarding embeddings module operations."""


class Error(Exception):
    """Base exception class."""


class FileIsNotAnIndex(Error):
    """Raised when a file is not recognized as an index file."""


class IndexNotBuildYet(Error):
    """Raised when an index is not built yet."""


class NoDataDirForPermanentIndex(Error):
    """Raised when a data directory isn't defined for a not volatile index."""


class DataDirDefinedForVolatileIndex(Error):
    """Raised when a data directory is defined for a volatile index."""


class NullTensorError(Error):
    """Raised when trying to insert a null (empty) tensor."""


class TopNegativeOrZero(Error):
    """Raised when the top results filter is zero or below."""


class EmptyIndexError(Error):
    """Raised when a loaded index is empty."""
