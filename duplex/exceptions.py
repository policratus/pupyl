"""
Exceptions regarding embeddings module operations
"""


class Error(Exception):
    """
    Base exception class
    """


class FileTypeNotSupportedYet(Error):
    """
    Raised when an unknown file type was discovered
    """


class FileIsNotImage(Error):
    """
    Raised when the analyzed file is not an image
    """
