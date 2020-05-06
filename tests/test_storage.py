"""Unit tests related to storage.database module."""
import os
import tempfile
from unittest import TestCase

import numpy

from storage.database import ImageDatabase, FileMode
from duplex.image import ImageIO


PATH = f'{tempfile.gettempdir()}/test_database.db'
TEST_DB = 'tests/test.db'
TEST_GROUP = 'images'
TEST_LOCAL = os.path.abspath('tests/test_image.jpg')
TEST_TENSOR = ImageIO.encoded_to_compressed_tensor(ImageIO.get(TEST_LOCAL))
TEST_NAME = 'test1'


class TestCases(TestCase):
    """Unit tests over special cases."""

    def test_get_unsuccessful(self):
        """Unit test for method get, unsuccessful case."""
        test_unknown_group = 'unknown'
        test_unknown_name = 'unknown'
        image_database = ImageDatabase(TEST_DB, FileMode.READ_ONLY)

        with self.assertRaises(KeyError):
            image_database.get(test_unknown_group, test_unknown_name)


def test__init__class_create():
    """Unit test for method __init__, create case."""
    with ImageDatabase(PATH, FileMode.CREATE):
        assert os.path.exists(PATH)

    os.remove(PATH)


def test__init__class_read_only_case():
    """
    Unit test for method __init__, read only case
    """
    with ImageDatabase(PATH, FileMode.READ_ONLY) as image_database:
        assert image_database.mode == 'r+'

    with ImageDatabase(PATH, FileMode.READ_ONLY) as image_database:
        assert image_database.mode == 'r'

    os.remove(PATH)


def test__init__class_read_write_case():
    """
    Unit test for method __init__, read only case
    """
    with ImageDatabase(PATH, FileMode.READ_WRITE) as image_database:
        assert os.path.exists(PATH) and \
            image_database.mode == 'r+'

    os.remove(PATH)


def test__resolve_mode_read_write():
    """
    Unit test for method _resolve_mode, read/write case
    """
    assert ImageDatabase._resolve_mode(FileMode.READ_WRITE) == 'r+'


def test__resolve_mode_unknown():
    """
    Unit test for method _resolve_mode, unknown case
    """
    test_case = 'UNKNOWN'
    assert ImageDatabase._resolve_mode(test_case) is FileMode.UNKNOWN


def test_get_successful():
    """
    Unit test for method get, successful case
    """
    image_database = ImageDatabase(TEST_DB, FileMode.READ_ONLY)

    numpy.testing.assert_array_equal(
        image_database.get(TEST_GROUP, TEST_NAME),
        TEST_TENSOR
        )


def test_add():
    """
    Unit test for method add
    """
    test_db = 'tests/test2.db'

    image_database = ImageDatabase(test_db, FileMode.READ_WRITE)

    image_database.add(TEST_GROUP, TEST_NAME, TEST_TENSOR)

    numpy.testing.assert_array_equal(
        image_database.get(TEST_GROUP, TEST_NAME),
        TEST_TENSOR
        )

    os.remove(test_db)
