"""
Unit tests related to duplex.image module
"""
from os.path import abspath
from unittest import TestCase

import numpy

from duplex.image import ImageIO, Protocols


TEST_URL = 'https://avatars1.githubusercontent.com/u/827563'
TEST_LOCAL = abspath('tests/test_image.jpg')
TEST_UNKNOWN = 'unk://path'
TEST_SIZE = (280, 260)
TEST_RESIZE = (100, 100)

IMAGE_IO = ImageIO()


def test__infer_protocol_http():
    """
    Unit tests for _infer_protocol method, http case
    """
    assert IMAGE_IO._infer_protocol(TEST_URL) is Protocols.HTTP


def test__infer_protocol_local():
    """
    Unit tests for _infer_protocol method, local case
    """
    assert IMAGE_IO._infer_protocol(TEST_LOCAL) is Protocols.FILE


def test__infer_protocol_unknown():
    """
    Unit tests for _infer_protocol method, unknown case
    """
    assert IMAGE_IO._infer_protocol(TEST_UNKNOWN) is Protocols.UNKNOWN


def test__get_url_succesful():
    """
    Unit tests for _get_url method, successful case
    """
    assert isinstance(IMAGE_IO._get_url(TEST_URL), numpy.ndarray)


def test__get_url_unsuccesful():
    """
    Unit tests for _get_url method, unsuccessful case
    """
    try:
        IMAGE_IO._get_url(TEST_UNKNOWN)
    except IOError:
        assert True


def test_get_http():
    """
    Unit test for get method, http case
    """
    assert isinstance(IMAGE_IO.get(TEST_URL), numpy.ndarray)


def test_get_local():
    """
    Unit test for get method, http case
    """
    assert isinstance(IMAGE_IO.get(TEST_LOCAL), numpy.ndarray)


def test__get_local_succesful():
    """
    Unit test for _get_local method, local succesful case
    """
    assert isinstance(IMAGE_IO._get_local(TEST_LOCAL), numpy.ndarray)


class TestCases(TestCase):
    """
    Unit tests over special cases
    """
    def test__get_local_unsuccesful(self):
        """
        Unit test for _get_local method, local unsuccesful case
        """
        with self.assertRaises(IOError):
            IMAGE_IO._get_local(TEST_UNKNOWN)


def test_get_unknown():
    """
    Unit test for get method, unknown case
    """
    assert IMAGE_IO.get(TEST_UNKNOWN) is Protocols.UNKNOWN


def test_size_size():
    """
    Unit test for size method, return size case
    """
    assert IMAGE_IO.size(TEST_LOCAL) == TEST_SIZE


def test_size_resize():
    """
    Unit test for size method, return size case
    """
    assert IMAGE_IO.size(TEST_LOCAL, TEST_RESIZE).shape[:2] == TEST_RESIZE
