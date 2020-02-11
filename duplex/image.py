"""
Image module

Performs multiple operations over images, like resizing,
loading and so on.
"""
from urllib.request import urlopen
from enum import Enum, auto

import numpy
from tensorflow import io as io_ops
from tensorflow import image as image_ops


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
        bytes or Enum:
            If succesful, returns the image bytes,
            or an Enum describing format not recognized
        """
        if cls._infer_protocol(uri) is Protocols.FILE:
            return cls._get_local(uri)

        if cls._infer_protocol(uri) is Protocols.HTTP:
            return cls._get_url(uri)

        return Protocols.UNKNOWN

    @classmethod
    def _get_url(cls, url):
        """
        Load an image from a remote (http(s)) location

        Parameters
        ----------
        url: str
            The URL where the image are stored

        Returns
        -------
        bytes:
            With image tensor
        """
        try:
            return urlopen(url).read()
        except IOError:
            raise IOError(f'Impossible to read image {url}')

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
        bytes:
            With image tensor
        """
        with open(path, 'rb') as image:
            return image.read()

    @staticmethod
    def encoded_to_compressed_tensor(encoded):
        """
        Transform a binary encoded string image
        to its compressed tensor

        Parameters
        ----------
        encoded: bytes
            The binary representation of the image

        Returns
        -------
        numpy.ndarray
        """
        return numpy.array(memoryview(io_ops.decode_raw(encoded, 'uint8')))

    @staticmethod
    def encoded_to_tensor(encoded):
        """
        Transform a binary encoded string image to tensor

        Parameters
        ----------
        encoded: bytes
            The binary representation of the image

        Returns
        -------
        numpy.ndarray
        """
        return numpy.array(memoryview(io_ops.decode_image(encoded)))

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
            return image_ops.resize(
                cls.encoded_to_tensor(cls.get(uri)),
                new_size,
                method=image_ops.ResizeMethod.NEAREST_NEIGHBOR
            )

        return cls.encoded_to_tensor(cls.get(uri)).shape[:2]

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
        return image_ops.encode_jpeg(
            tensor,
            quality=90,
            progressive=True,
            optimize_size=True,
            chroma_downsampling=True
        )
