"""
Image module

Performs multiple operations over images, like resizing,
loading and so on.
"""
from urllib.request import urlopen
from enum import Enum, auto

import numpy
import cv2


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
            image = cv2.imdecode(
                numpy.asarray(
                    bytearray(
                        urlopen(url).read()
                    )
                ),
                cv2.IMREAD_COLOR
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
        image = cv2.imread(path, cv2.IMREAD_COLOR)

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
            return cv2.resize(cls.get(uri), new_size)

        return cls.get(uri).shape[:2]

    @staticmethod
    def compress(tensor):
        """
        Compress the tensor before saving it

        Parameters
        ----------
        tensor: numpy.ndarray
            A tensor representing an image

        Returns
        -------
        numpy.ndarray
            An encoded image
        """
        _, encoded = cv2.imencode(
            '.webp',
            tensor,
            (
                cv2.IMWRITE_WEBP_QUALITY,
                80
            )
        )

        return encoded

    @staticmethod
    def decompress(tensor):
        """
        Decompress a tensor before loading it

        Parameters
        ----------
        tensor: numpy.ndarray
            A tensor representing an encoded image

        Returns
        -------
        numpy.ndarray
            A decoded image
        """
        return cv2.imdecode(tensor, cv2.IMREAD_UNCHANGED)
