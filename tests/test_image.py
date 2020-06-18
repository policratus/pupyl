"""Unit tests related to duplex.image module."""
import tempfile
from os.path import abspath
from unittest import TestCase

import numpy
from tensorflow import io as io_ops

from duplex.image import ImageIO
from duplex.exceptions import FileIsNotImage


TEST_URL = 'https://upload.wikimedia.org/wikipedia/commons/thumb/e/e4/' + \
    'Cheshm-Nazar.JPG/320px-Cheshm-Nazar.JPG'
TEST_LOCAL = abspath('tests/test_image.jpg')
TEST_NOT_IMAGE = abspath('tests/not_image.txt')
TEST_SAVED_TENSOR = abspath('tests/compressed_image.npy')
TEST_SIZE = (280, 260)
TEST_RESIZE = (100, 100)


class TestCases(TestCase):
    """Unit tests over special cases."""

    def test_get_image_no_image(self):
        """Unit test for get_image method, not image case."""
        with self.assertRaises(FileIsNotImage):
            ImageIO.get_image(TEST_NOT_IMAGE)


def test_get_image_as_tensor():
    """
    Unit test for get_image method, as_tensor optional parameter set
    """
    assert isinstance(
        ImageIO.get_image(TEST_LOCAL, as_tensor=True), numpy.ndarray)


def test_size_size():
    """
    Unit test for size method, return size case
    """
    assert ImageIO.size(TEST_LOCAL) == TEST_SIZE


def test_size_resize():
    """
    Unit test for size method, return size case
    """
    assert ImageIO.size(TEST_LOCAL, TEST_RESIZE).shape[:2] == TEST_RESIZE


def test_compress():
    """
    Unit test for compress method
    """
    def behaviour_compress(tensor):
        """
        Closure with expected behaviour for compress
        method
        """
        return io_ops.encode_jpeg(
            tensor,
            quality=80,
            progressive=True,
            optimize_size=True,
            chroma_downsampling=True
            )

    test_image_bytes = ImageIO.get_image(TEST_LOCAL)
    test_tensor = ImageIO.encoded_to_tensor(test_image_bytes)

    numpy.testing.assert_array_equal(
        ImageIO.compress(test_tensor),
        behaviour_compress(test_tensor)
        )

    numpy.testing.assert_array_equal(
        ImageIO.compress(test_tensor, as_tensor=True),
        ImageIO.encoded_to_tensor(behaviour_compress(test_tensor))
    )


def test_encoded_to_compressed_tensor():
    """Unit test for encoded_to_compressed_tensor method."""
    saved_tensor = numpy.load(TEST_SAVED_TENSOR, allow_pickle=False)
    test_tensor = ImageIO.encoded_to_compressed_tensor(
        ImageIO.get_image(TEST_LOCAL)
        )

    assert test_tensor.ndim == 1 and test_tensor.size == 6104
    numpy.testing.assert_array_equal(saved_tensor, test_tensor)


def test_save_image():
    """Unit test for save_image method."""
    test_tensor_bytes = ImageIO.get_image(TEST_LOCAL)

    with tempfile.NamedTemporaryFile() as temp_file:
        ImageIO.save_image(temp_file.name, test_tensor_bytes)

        assert test_tensor_bytes == ImageIO.get_image(temp_file.name)
