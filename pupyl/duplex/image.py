"""Performs multiple operations over images, like resizing,loading and so on"""

from base64 import b64encode

from pupyl.verbosity import quiet_tf
quiet_tf()

import tensorflow
from tensorflow import image as image_ops
from tensorflow import io as io_ops

from pupyl.duplex.exceptions import FileIsNotImage
from pupyl.duplex.file_io import FileIO


class ImageIO(FileIO):
    """Operations of read and write over images."""

    @staticmethod
    def encoded_to_compressed_tensor(encoded):
        """Transforms a binary encoded string image to its compressed tensor
        form.

        Parameters
        ----------
        encoded: bytes
            The binary representation of the image.

        Returns
        -------
        numpy.ndarray
            The actual compressed image tensor.
        """
        return io_ops.decode_raw(encoded, 'uint8')

    @staticmethod
    def encoded_to_tensor(encoded):
        """Transforms a binary encoded string image to a tensor.

        Parameters
        ----------
        encoded: bytes
            The binary representation of the image.

        Returns
        -------
        numpy.ndarray
            Describing the compressed image tensor.
        """
        return io_ops.decode_image(encoded)

    @classmethod
    def get_image(cls, uri, as_tensor=False):
        """Loads an image from a specified location.

        Parameters
        ----------
        uri: str
            Location where the image are stored.

        as_tensor: bool
            If the image should be converted to its tensor representation.
            Defaults to False, which returns images to a byte representation

        Returns
        -------
        bytes or numpy.ndarray
            Respectively returns the image as bytes or as a tensor
            representation.
        """
        bytess = cls.get(uri)

        if cls.is_image(bytess):
            if as_tensor:
                tensor = cls.encoded_to_tensor(bytess)

                last_dimensions = tensor.get_shape()[-1]

                if last_dimensions == 1:
                    tensor = image_ops.grayscale_to_rgb(tensor)
                elif last_dimensions == 4:
                    tensor = io_ops.decode_png(bytess, channels=3)

                tensor = tensorflow.dtypes.cast(
                    tensor,
                    tensorflow.float32
                )

                return tensor

            return bytess

        raise FileIsNotImage

    @classmethod
    def get_image_base64(cls, uri):
        """Loads an image as a base64 encoded string.

        Parameters
        ----------
        uri: str
            Location where the image is stored.

        Returns
        -------
        bytes:
            The base64 encoded image format.
        """
        return b64encode(cls.get_image(uri, as_tensor=False))

    def scan_images(self, uri):
        """
        Scans a source looking for images.

        Parameters
        ----------
        uri: str
            Location where the source is stored.

        Yields
        ------
        str:
            The validated image file on the passed ``uri``.
        """
        for ffile in self.scan(uri):
            file_bytes = self.get(ffile)

            if self.is_image(file_bytes):
                yield ffile

    @classmethod
    def get_image_bytes_to_base64(cls, image_bytes):
        """Returns the image representation in base64, from its
        bytes representation.

        Parameters
        ----------
        image_bytes: bytes
            Bytes representation of some image.

        Raises
        ------
        FileIsNotImage:
            If the file is not recognized as an image.

        Returns
        -------
        bytes:
            The base64 encoded image format.
        """
        if cls.is_image(image_bytes):
            return b64encode(image_bytes)

        raise FileIsNotImage

    @staticmethod
    def save_image(path, bytess):
        """Saves an image to a defined path.

        Parameters
        ----------
        path: str
            Local to save the image.

        bytess: bytes
            Bytes representing an image.
        """
        io_ops.write_file(path, bytess)

    @classmethod
    def size(cls, uri, new_size=None, keep_aspect=False):
        """Returns the current image dimensions or resize it.

        Parameters
        ----------
        uri: str
            Description of where the image are located

        new_size: tuple
            The new intended dimension of the image

        keep_aspect: bool
            If the image proportions should be preserved
            or not.

        Returns
        -------
        tuple or numpy.ndarray:
            Respectively with current image dimensions or if new_size is
            ``True``, a resized image, if ``new_size`` parameter was passed
            through.
        """
        if new_size:
            return image_ops.resize(
                cls.get_image(uri, as_tensor=True),
                new_size,
                method=image_ops.ResizeMethod.NEAREST_NEIGHBOR,
                preserve_aspect_ratio=keep_aspect
            )

        return cls.get_image(uri, as_tensor=True).shape[:2]

    @classmethod
    def compress(cls, tensor, as_tensor=False):
        """Compress the tensor using the JPEG algorithm.

        Parameters
        ----------
        tensor: numpy.ndarray
            A tensor representing an image

        as_tensor: bool
            If the new compressed JPEG image should be
            returned as a ``numpy.ndarray``.

        Returns
        -------
        bytes or numpy.ndarray:
            An encoded image, in bytes or a tensor in numpy.ndarray
        """
        if tensor.dtype is not tensorflow.uint8:
            tensor = tensorflow.dtypes.cast(
                tensor,
                tensorflow.uint8
            )

        compressed = image_ops.encode_jpeg(
            tensor,
            quality=80,
            progressive=True,
            optimize_size=True,
            chroma_downsampling=True
        )

        if as_tensor:
            return cls.encoded_to_tensor(compressed)

        return compressed
