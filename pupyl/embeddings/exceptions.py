"""Exceptions regarding embeddings module operations"""


class Error(Exception):
    """Base exception class"""


class UnknownCharacteristics(Error):
    """Raised when a not known network characteristic is passed"""


class UnknownCharacteristicsValue(Error):
    """Raised when a not known value for a characteristic is passed"""


class UnknownCharacteristicsName(Error):
    """Raised when a not known name for a characteristic is passed"""
