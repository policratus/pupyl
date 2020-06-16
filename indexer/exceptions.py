"""
Exceptions regarding embeddings module operations
"""


class Error(Exception):
    """
    Base exception class
    """


class FileIsNotAnIndex(Error):
    """
    Raised when a file is not recognized as a index file.
    """


class IndexNotBuildYet(Error):
    """
    Raised when a file is not recognized as a index file.
    """


class NoDataDirForPermanentIndex(Error):
    """
    Raised when a data directory isn't defined for a not volatile index.
    """


class DataDirDefinedForVolatileIndex(Error):
    """
    Raised when a data directory is defined for a volatile index.
    """


class NullTensorError(Error):
    """
    Raised when trying to insert a null tensor.
    """
