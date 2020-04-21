"""
Image module.

Performs multiple operations over images, like resizing,
loading and so on.
"""
import numpy
from tensorflow import io as io_ops
from tensorflow import image as image_ops

from duplex.file_io import FileIO
from duplex.file_types import FileType
from duplex.exceptions import FileIsNotImage


class ImageIO(FileIO, FileType):
    """Operations of read and write over images."""

    @staticmethod
    def encoded_to_compressed_tensor(encoded):
        """
        Transform a binary encoded string image to its compressed tensor.

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
        Transform a binary encoded string image to tensor.

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
    def get_image(cls, uri, as_tensor=False):
        """
        Load a image from specified location.

        Parameters
        ----------
        uri: str
            Location where the image are stored

        as_tensor (optional): bool
            Default: False

            If the image should be converted to its tensor representation.
            Default to False, which returns images to byte representation

        Returns
        -------
        bytes or numpy.ndarray
            Respectively returns the image as bytes or as tensor
            representation
        """
        bytess = cls.get(uri)

        if cls.is_image(bytess):
            if as_tensor:
                return cls.encoded_to_tensor(bytess)

            return bytess

        raise FileIsNotImage

    @classmethod
    def size(cls, uri, new_size=None):
        """
        Return the current image dimensions or resize it.

        Parameters
        ----------
        uri: str
            Description of where the image are located

        new_size (optional): tuple
            The new intended dimension of the image

        Returns
        -------
        tuple:
            Current image dimensions

        If new_size is True:
            numpy.ndarray:
                A resized image, if new_size parameter
                was passed through
        """
        if new_size:
            return numpy.array(
                memoryview(
                    image_ops.resize(
                        cls.get_image(uri, as_tensor=True),
                        new_size,
                        method=image_ops.ResizeMethod.NEAREST_NEIGHBOR
                        )
                    )
                )

        return cls.get_image(uri, as_tensor=True).shape[:2]

    @staticmethod
    def compress(tensor):
        """
        Compress the tensor before saving it, as JPEG.

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
