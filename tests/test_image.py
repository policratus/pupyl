"""
Unit tests related to duplex.image module
"""
from os.path import abspath
from unittest import TestCase

import numpy
from tensorflow import io as io_ops

from duplex.image import ImageIO, Protocols


TEST_URL = 'https://avatars1.githubusercontent.com/u/827563'
TEST_LOCAL = abspath('tests/test_image.jpg')
TEST_UNKNOWN = 'unk://path'
TEST_SIZE = (280, 260)
TEST_RESIZE = (100, 100)


class TestCases(TestCase):
    """
    Unit tests over special cases
    """
    def test__get_local_unsuccessful(self):
        """
        Unit test for _get_local method, local unsuccessful case
        """
        with self.assertRaises(IOError):
            ImageIO._get_local(TEST_UNKNOWN)


def test__infer_protocol_http():
    """
    Unit tests for _infer_protocol method, http case
    """
    assert ImageIO._infer_protocol(TEST_URL) is Protocols.HTTP


def test__infer_protocol_local():
    """
    Unit tests for _infer_protocol method, local case
    """
    assert ImageIO._infer_protocol(TEST_LOCAL) is Protocols.FILE


def test__infer_protocol_unknown():
    """
    Unit tests for _infer_protocol method, unknown case
    """
    assert ImageIO._infer_protocol(TEST_UNKNOWN) is Protocols.UNKNOWN


def test__get_url_successful():
    """
    Unit tests for _get_url method, successful case
    """
    assert isinstance(ImageIO._get_url(TEST_URL), bytes)


def test__get_url_unsuccessful():
    """
    Unit tests for _get_url method, unsuccessful case
    """
    try:
        ImageIO._get_url(TEST_UNKNOWN)
    except IOError:
        assert True


def test_get_http():
    """
    Unit test for get method, http case
    """
    assert isinstance(ImageIO.get(TEST_URL), bytes)


def test_get_local():
    """
    Unit test for get method, http case
    """
    assert isinstance(ImageIO.get(TEST_LOCAL), bytes)


def test__get_local_successful():
    """
    Unit test for _get_local method, local successful case
    """
    assert isinstance(ImageIO._get_local(TEST_LOCAL), bytes)


def test_get_as_tensor():
    """
    Unit test for get method, as_tensor optional parameter set
    """
    assert isinstance(ImageIO.get(TEST_LOCAL, as_tensor=True), numpy.ndarray)


def test_get_unknown():
    """
    Unit test for get method, unknown case
    """
    assert ImageIO.get(TEST_UNKNOWN) is Protocols.UNKNOWN


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

    test_tensor = ImageIO.encoded_to_tensor(ImageIO.get(TEST_LOCAL))

    assert numpy.equal(
        ImageIO.compress(test_tensor),
        behaviour_compress(test_tensor)
    )
