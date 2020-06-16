"""Unit tests related to indexer.facets module."""
import os
from unittest import TestCase

import numpy

from indexer.facets import Index
from indexer.exceptions import FileIsNotAnIndex, IndexNotBuildYet, \
    NoDataDirForPermanentIndex, DataDirDefinedForVolatileIndex, \
    NullTensorError
from duplex.file_io import FileIO


TEST_INDEX_PATH = os.path.abspath('tests/')
TEST_INDEX_SEARCH_PATH = os.path.join(TEST_INDEX_PATH, 'test_search/')
TEST_INDEX_INVALID_FILE = os.path.abspath('tests/test_index/')
TEST_VECTOR_SIZE = 128

INDEX = Index(TEST_VECTOR_SIZE, TEST_INDEX_PATH)
ALL_ITEMS = list(INDEX.items())
ALL_VALUES = list(INDEX.values())


class TestCases(TestCase):
    """Unit tests over special cases."""

    def test___next_stop_iteration(self):
        """Unit test for method __next__, StopIteration case."""
        with self.assertRaises(StopIteration):
            index = Index(TEST_VECTOR_SIZE, TEST_INDEX_PATH)
            while True:
                next(index)

    def test_open_invalid_file(self):
        """Unit test for method __init__, invalid file case."""
        with self.assertRaises(FileIsNotAnIndex):
            Index(TEST_VECTOR_SIZE, TEST_INDEX_INVALID_FILE)

    def test_remove_new_file(self):
        """Unit test for method remove, new file case."""
        with self.assertRaises(IndexNotBuildYet):
            with Index(size=8, volatile=True) as index:
                index.remove(0)

    def test_data_dir_is_not_a_dir(self):
        """Unit test for __init__, data dir. as file case."""
        with self.assertRaises(OSError):
            Index(
                TEST_VECTOR_SIZE,
                os.path.join(TEST_INDEX_PATH, 'pupyl.index')
            )

    def test_no_data_dir_for_perm_file(self):
        """Unit test for __init__, no data dir for perm. file case."""
        with self.assertRaises(NoDataDirForPermanentIndex):
            Index(TEST_VECTOR_SIZE, data_dir=None)

    def test_data_dir_for_volatile_file(self):
        """Unit test for __init__, data dir for volatile file case."""
        with self.assertRaises(DataDirDefinedForVolatileIndex):
            Index(
                TEST_VECTOR_SIZE,
                data_dir=os.path.join(TEST_INDEX_PATH, 'pupyl.index'),
                volatile=True
            )

    def test_raises_null_tensor_error(self):
        """Unit test for append, null tensor case."""
        with self.assertRaises(NullTensorError):
            with Index(TEST_VECTOR_SIZE, volatile=True) as index:
                index.append(numpy.zeros(shape=TEST_VECTOR_SIZE))

    def test_remove_index_error(self):
        """Unit test for remove, index error case."""
        with self.assertRaises(IndexError):
            INDEX.remove(999)


def test_open_index():
    """Unit test for index opening."""
    assert INDEX.size == TEST_VECTOR_SIZE


def test_context():
    """Unit test to test context opening and close."""
    with Index(TEST_VECTOR_SIZE, TEST_INDEX_PATH) as index:
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
    assert INDEX.path == os.path.join(TEST_INDEX_PATH, INDEX.index_name)


def test_trees_property():
    """Unit test for path property."""
    assert INDEX.trees == .001


def test_volatile_property():
    """Unit test for volatile property."""
    assert not INDEX.volatile


def test_trees_property_setter():
    """Unit test for path property."""
    INDEX.trees = 1

    assert INDEX.trees == 1


def test_open_new_index():
    """Unit test for new index opening."""
    with Index(TEST_VECTOR_SIZE, volatile=True) as index:
        assert index.size == TEST_VECTOR_SIZE


def test_append_new_file():
    """Unit test for method append, new file case."""
    with Index(TEST_VECTOR_SIZE, volatile=True) as index:

        test_size_before = len(index)
        new_tensor = numpy.random.normal(size=TEST_VECTOR_SIZE)

        index.append(new_tensor)

        test_size_after = len(index)

        assert test_size_after == test_size_before + 1

        numpy.testing.assert_array_almost_equal(
            index[-1], new_tensor, decimal=7
            )


def test_append_new_created_file():
    """Unit test for method append, created file case."""
    test_size_before = len(INDEX)
    new_tensor = numpy.random.normal(size=TEST_VECTOR_SIZE)

    INDEX.append(new_tensor)

    test_size_after = len(INDEX)

    assert test_size_after == test_size_before + 1

    numpy.testing.assert_array_almost_equal(
        INDEX[-1], new_tensor, decimal=7
        )


def test_remove():
    """Unit test for method remove."""
    index_to_remove = 8

    temp_file = FileIO.safe_temp_file(file_name='pupyl.index')
    temp_dir = os.path.dirname(temp_file)

    with Index(TEST_VECTOR_SIZE, data_dir=temp_dir) as index:
        for _ in range(16):
            index.append(numpy.random.normal(size=TEST_VECTOR_SIZE))

        test_size_before = len(index)

        test_value = index[index_to_remove]

    with Index(TEST_VECTOR_SIZE, data_dir=temp_dir) as index:
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
    temp_file = FileIO.safe_temp_file(file_name='pupyl.index')
    temp_dir = os.path.dirname(temp_file)

    with Index(TEST_VECTOR_SIZE, data_dir=temp_dir) as index:
        for _ in range(16):
            index.append(numpy.random.normal(size=TEST_VECTOR_SIZE))

        test_size_before = len(index)

        test_value_before = index[-1]

    with Index(TEST_VECTOR_SIZE, data_dir=temp_dir) as index:
        test_value_after = index.pop()

        assert len(index) == test_size_before - 1

        numpy.testing.assert_array_equal(
            test_value_before,
            test_value_after
        )


def test_pop_index():
    """Unit test for method pop, index case."""
    index_to_pop = 4

    temp_file = FileIO.safe_temp_file(file_name='pupyl.index')
    temp_dir = os.path.dirname(temp_file)

    with Index(TEST_VECTOR_SIZE, data_dir=temp_dir) as index:
        for _ in range(16):
            index.append(numpy.random.normal(size=TEST_VECTOR_SIZE))

        test_size_before = len(index)

        test_value_before = index[index_to_pop]

    with Index(TEST_VECTOR_SIZE, data_dir=temp_dir) as index:
        test_value_after = index.pop(index_to_pop)

        assert len(index) == test_size_before - 1

        numpy.testing.assert_array_equal(
            test_value_before,
            test_value_after
        )


def test_index():
    """Unit test for method index."""
    test_position = 0

    with Index(TEST_VECTOR_SIZE, TEST_INDEX_PATH) as index:
        test_value = index[test_position]

        assert index.index(test_value) == 0


def test_search():
    """Unit test for method search."""
    query_array = [-0.48870765, -0.57780915, -0.94986234, -1.90035123]
    expected_search_result = [25, 78]

    with Index(len(query_array), TEST_INDEX_SEARCH_PATH) as index:
        test_result = [*index.search(query_array, results=2)]

    assert expected_search_result == test_result