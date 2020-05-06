"""Unit tests related to indexer.facets module."""
import os
import tempfile
from unittest import TestCase

import numpy

from duplex.file_io import FileIO
from indexer.facets import Index
from indexer.exceptions import FileIsNotAnIndex, IndexNotBuildYet


TEST_VECTOR_PATH = os.path.abspath('tests/test.idx')
TEST_VECTOR_TEMP_FILE = f'{tempfile.gettempdir()}/temp.idx'
TEST_VECTOR_INVALID_FILE = os.path.abspath('tests/not_image.txt')
TEST_VECTOR_SIZE = 128

INDEX = Index(TEST_VECTOR_PATH, TEST_VECTOR_SIZE)
ALL_ITEMS = list(INDEX.items())
ALL_VALUES = list(INDEX.values())


class TestCases(TestCase):
    """Unit tests over special cases."""

    def test___next_stop_iteration(self):
        """Unit test for method __next__, StopIteration case."""
        with self.assertRaises(StopIteration):
            index = Index(TEST_VECTOR_PATH, TEST_VECTOR_SIZE)
            while True:
                next(index)

    def test_open_invalid_file(self):
        """Unit test for method __init__, invalid file case."""
        with self.assertRaises(FileIsNotAnIndex):
            Index(TEST_VECTOR_INVALID_FILE, TEST_VECTOR_SIZE)

    def test_remove_new_file(self):
        """Unit test for method remove, new file case."""
        with self.assertRaises(IndexNotBuildYet):
            tmp_file = FileIO.safe_temp_file()

            with Index(tmp_file, 8) as index:
                index.remove(0)


def test_open_index():
    """Unit test for index opening."""
    assert INDEX.size == TEST_VECTOR_SIZE


def test_context():
    """Unit test to test context opening and close."""
    with Index(TEST_VECTOR_PATH, TEST_VECTOR_SIZE) as index:
        assert isinstance(index, Index)


def test_items():
    """Unit test for method items."""
    for test_item, method_item in zip(ALL_ITEMS, INDEX.items()):
        assert test_item == method_item


def test_values():
    """Unit test for method items."""
    for test_value, method_value in zip(ALL_VALUES, INDEX.values()):
        assert test_value == method_value


def test_items_values():
    """Unit test for method items_values."""
    for items_values, test_item, test_value in zip(
            INDEX.items_values(), ALL_ITEMS, ALL_VALUES
            ):
        method_item, method_value = items_values

        assert test_item == method_item and \
            test_value == method_value


def test___get_item__():
    """Unit test for magic method __getitem__."""
    assert INDEX[0] == ALL_VALUES[0]


def test_reversed__get_item__():
    """Unit test for magic method __getitem__, reversed case."""
    assert INDEX[-1] == ALL_VALUES[-1]


def test___len__():
    """Unit test for magic method __len__"""
    assert len(INDEX) == len(ALL_ITEMS)


def test___iter__():
    """Unit test for magic method __iter__"""
    for test_value, method_value in zip(ALL_VALUES, INDEX):
        assert test_value == method_value


def test___next__():
    """Unit test for magic method __next__"""
    for value in ALL_VALUES:
        assert next(INDEX) == value


def test_size():
    """Unit test for method size."""
    assert INDEX.size == TEST_VECTOR_SIZE


def test_path_property():
    """Unit test for path property."""
    assert INDEX.path == TEST_VECTOR_PATH


def test_trees_property():
    """Unit test for path property."""
    assert INDEX.trees == .001


def test_trees_property_setter():
    """Unit test for path property."""
    INDEX.trees = 1

    assert INDEX.trees == 1


def test_open_new_index():
    """Unit test for new index opening."""
    with Index(TEST_VECTOR_TEMP_FILE, TEST_VECTOR_SIZE) as index:
        assert index.size == TEST_VECTOR_SIZE


def test_append():
    """Unit test for method safe_temp_file."""
    with Index(TEST_VECTOR_TEMP_FILE, TEST_VECTOR_SIZE) as index:

        test_size_before = len(index)
        new_tensor = numpy.random.normal(size=TEST_VECTOR_SIZE)

        index.append(new_tensor)

    with Index(TEST_VECTOR_TEMP_FILE, TEST_VECTOR_SIZE) as index:

        test_size_after = len(index)

        assert test_size_after == test_size_before + 1

        numpy.testing.assert_array_almost_equal(
            index[-1], new_tensor, decimal=7
            )


def test_save():
    """Unit test for method save."""
    with Index(TEST_VECTOR_TEMP_FILE, TEST_VECTOR_SIZE) as index:

        new_tensor = numpy.random.normal(size=TEST_VECTOR_SIZE)

        index.append(new_tensor)

    with Index(TEST_VECTOR_TEMP_FILE, TEST_VECTOR_SIZE) as index:
        numpy.testing.assert_array_almost_equal(
            index[-1], new_tensor, decimal=7
            )


def test_remove():
    """Unit test for method remove."""
    index_to_remove = 0

    with Index(TEST_VECTOR_TEMP_FILE, TEST_VECTOR_SIZE) as index:
        new_tensor = numpy.random.normal(size=TEST_VECTOR_SIZE)
        index.append(new_tensor)

    with Index(TEST_VECTOR_TEMP_FILE, TEST_VECTOR_SIZE) as index:
        test_size_before = len(index)
        test_value = index[index_to_remove]

        index.remove(index_to_remove)

        assert len(index) == test_size_before - 1

        numpy.testing.assert_raises(
            AssertionError,
            numpy.testing.assert_array_equal,
            test_value,
            index[index_to_remove]
            )


def test_pop():
    """Unit test for method pop."""
    with Index(TEST_VECTOR_TEMP_FILE, TEST_VECTOR_SIZE) as index:
        new_tensor = numpy.random.normal(size=TEST_VECTOR_SIZE)
        index.append(new_tensor)

    with Index(TEST_VECTOR_TEMP_FILE, TEST_VECTOR_SIZE) as index:
        test_size_before = len(index)

        popped_value = index.pop()

        assert len(index) == test_size_before - 1

        numpy.testing.assert_raises(
            AssertionError,
            numpy.testing.assert_array_equal,
            popped_value,
            index[-1]
            )


def test_index():
    """Unit test for method index."""
    test_position = 0

    with Index(TEST_VECTOR_PATH, TEST_VECTOR_SIZE) as index:
        test_value = index[test_position]

        assert index.index(test_value) == 0


def test_search():
    """Unit test for method search."""
    expected_search_result = [0, 4, 2, 3, 1, 9, 7, 8, 6, 5]

    with Index(TEST_VECTOR_PATH, TEST_VECTOR_SIZE) as index:
        test_value = index[0]

        test_result = [*index.search(test_value)]

    assert expected_search_result == test_result
