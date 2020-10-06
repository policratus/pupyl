"""
Exceptions regarding embeddings module operations
"""


class Error(Exception):
    """
    Base exception class
    """


class UnknownCharacteristics(Error):
    """
    Raised when a not known network characteristic is passed
    """
