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
