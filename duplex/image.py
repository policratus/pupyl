"""
Image module

Performs multiple operations over images, like resizing,
loading and so on.
"""
from urllib.request import urlopen
from enum import Enum, auto

import numpy
from cv2 import imread, IMREAD_COLOR, resize, imdecode


class Protocols(Enum):
    """
    Defines several possible protocols to be discovered
    """
    UNKNOWN = auto()
    HTTP = auto()
    FILE = auto()


class ImageIO:
    """
    Operations of read and write over images
    """
    @staticmethod
    def _infer_protocol(uri):
        """
        Discover the protocol which the passed uri may pertain

        Parameters
        ----------
        uri: str
            URI that describes the image location

        Returns
        -------
        Enum:
            Referencing the discovered protocol
        """
        if uri.startswith('http'):
            return Protocols.HTTP

        if uri.startswith('file') or uri[0] == '/':
            return Protocols.FILE

        return Protocols.UNKNOWN

    @classmethod
    def get(cls, uri):
        """
        Load an image file from specified location

        Parameters
        ----------
        uri: str
            Location where the image are stored

        Returns
        -------
        numpy.ndarray or Enum:
            If succesful, returns the image tensor,
            or an Enum describing format not recognized
        """
        if cls._infer_protocol(uri) is Protocols.FILE:
            return cls._get_local(uri)

        if cls._infer_protocol(uri) is Protocols.HTTP:
            return cls._get_url(uri)

        return Protocols.UNKNOWN

    @staticmethod
    def _get_url(url):
        """
        Load an image from a remote (http(s)) location

        Parameters
        ----------
        url: str
            The URL where the image are stored

        Returns
        -------
        numpy.ndarray
            With image tensor
        """
        try:
            image = imdecode(
                numpy.asarray(
                    bytearray(
                        urlopen(url).read()
                    )
                ),
                IMREAD_COLOR
            )
        except IOError:
            raise IOError(f'Impossible to read image {url}')

        return image

    @staticmethod
    def _get_local(path):
        """
        Load an image from a local file

        Parameters
        ----------
        path: str
            Local which the image file is saved

        Returns
        -------
        numpy.ndarray
            With image tensor
        """
        image = imread(path, IMREAD_COLOR)

        if image is None:
            raise IOError(f'Impossible to read image {path}')

        return image

    @classmethod
    def size(cls, uri, new_size=None):
        """
        Returns the current image dimensions or
        resize it.

        Parameters
        ----------
        uri: str
            Description of where the image are located

        new_size: tuple
            The new intended dimension

        Returns
        -------
        tuple:
            Current image dimensions

        numpy.ndarray:
            A resized image
        """
        if new_size:
            return resize(cls.get(uri), new_size)

        return cls.get(uri).shape[:2]
