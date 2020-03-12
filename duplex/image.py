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
    def get(cls, uri, as_tensor=False):
        """
        Load an image file from specified location

        Parameters
        ----------
        uri: str
            Location where the image are stored

        as_tensor (optional): bool
            If the image should be converted to its tensor representation.
            Default to False, which returns images to byte representation

        Returns
        -------
        bytes or Enum:
            If successful, returns the image bytes,
            or an Enum describing format not recognized
        """
        if cls._infer_protocol(uri) is Protocols.FILE:
            image_bytes = cls._get_local(uri)
        elif cls._infer_protocol(uri) is Protocols.HTTP:
            image_bytes = cls._get_url(uri)
        else:
            return Protocols.UNKNOWN

        if as_tensor:
            return cls.encoded_to_tensor(image_bytes)

        return image_bytes

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
            With image binary information
        """
        return urlopen(url).read()

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
            With image binary information
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
            Describing the compressed image tensor
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
            The new intended dimension of the image

        Returns
        -------
        tuple:
            Current image dimensions

        If new_size as True:
            numpy.ndarray:
                A resized image, if new_size parameter
                is passed through
        """
        if new_size:
            return numpy.array(
                memoryview(
                    image_ops.resize(
                        cls.get(uri, as_tensor=True),
                        new_size,
                        method=image_ops.ResizeMethod.NEAREST_NEIGHBOR
                    )
                )
            )

        return cls.get(uri, as_tensor=True).shape[:2]

    @staticmethod
    def compress(tensor):
        """
        Compress the tensor before saving it,
        as a JPEG

        Parameters
        ----------
        tensor: numpy.ndarray
            A tensor representing an image

        Returns
        -------
        numpy.ndarray
            An encoded image, in bytes
        """
        return numpy.array(
            memoryview(
                image_ops.encode_jpeg(
                    tensor,
                    quality=80,
                    progressive=True,
                    optimize_size=True,
                    chroma_downsampling=True
                )
            )
        )
