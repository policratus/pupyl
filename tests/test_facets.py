"""Unit tests related to indexer.facets module."""
import os
import tempfile
import warnings
from platform import system
from unittest import TestCase

import numpy

from pupyl.indexer.facets import Index
from pupyl.indexer.exceptions import FileIsNotAnIndex, IndexNotBuildYet, \
    NoDataDirForPermanentIndex, DataDirDefinedForVolatileIndex, \
    NullTensorError, TopNegativeOrZero, EmptyIndexError, ExportIdsAndNames
from pupyl.duplex.file_io import FileIO
from pupyl.search import PupylImageSearch
from pupyl.embeddings.features import Extractors, Characteristics


TEST_INDEX_PATH = os.path.abspath('tests')
TEST_INDEX_SEARCH_PATH = os.path.join(TEST_INDEX_PATH, 'test_search')
TEST_INDEX_INVALID_FILE = os.path.join(TEST_INDEX_PATH, 'test_index')
TEST_INDEX_EXPORT = os.path.join(TEST_INDEX_PATH, 'test_index_export')
TEST_EMPTY_INDEX = os.path.join(TEST_INDEX_PATH, 'test_empty_index')
TEST_CHECK_UNIQUE = os.path.join(TEST_INDEX_PATH, 'test_check_unique')
TEST_ANIMATED_GIF = os.path.join(TEST_INDEX_PATH, 'test_gif.gif')
TEST_VECTOR_SIZE = 128

# INDEX = Index(TEST_VECTOR_SIZE, TEST_INDEX_PATH)
# ALL_ITEMS = list(INDEX.items())
# ALL_VALUES = list(INDEX.values())


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
        with self.assertRaises(IndexError), \
                Index(TEST_VECTOR_SIZE, TEST_INDEX_PATH) as index:
            index.remove(999)

    def test_negative_top(self):
        """Unit test for top parameter, negative case."""

        with self.assertRaises(TopNegativeOrZero):
            with Index(4, TEST_INDEX_SEARCH_PATH) as index:
                _ = [*index.group_by(top=-1)]

    def test_empty_index(self):
        """Unit test for an empty index."""
        with self.assertRaises(EmptyIndexError):
            with Index(1, TEST_EMPTY_INDEX) as index:
                _ = [*index.group_by()]

    def test_export_exclusive_options(self):
        """Unit test for exclusive options."""
        test_vector_size = 1024

        def export_routines(temp_dir, new_temp_dir):
            """Closure to support export routines test."""
            test_search = PupylImageSearch(temp_dir)

            test_search.index(TEST_INDEX_EXPORT)

            with Index(
                test_vector_size, data_dir=temp_dir
            ) as index:
                index.export_results(
                    new_temp_dir,
                    test_search.search(
                        os.path.join(TEST_INDEX_EXPORT, '1.jpg')
                    ),
                    keep_ids=True,
                    keep_names=True
                )

        with self.assertRaises(ExportIdsAndNames):
            # Windows: bypass clean up errors
            if system() == 'Windows':
                temp_dir = tempfile.TemporaryDirectory()
                new_temp_dir = tempfile.TemporaryDirectory()

                export_routines(temp_dir.name, new_temp_dir.name)

                temp_dir.cleanup()
                new_temp_dir.cleanup()
            else:
                with tempfile.TemporaryDirectory() as temp_dir, \
                        tempfile.TemporaryDirectory() as new_temp_dir:
                    export_routines(temp_dir.name, new_temp_dir.name)


def test_append_check_unique():
    """Unit test for method append, check unique case."""
    with warnings.catch_warnings(record=True) as caught_warnings:
        warnings.simplefilter('always')

        with Extractors(
            Characteristics.MINIMUMWEIGHT_FAST_SMALL_PRECISION
        ) as extractor, \
                Index(extractor.output_shape, volatile=True) as index:
            for image in extractor.scan(TEST_CHECK_UNIQUE):
                index.append(
                    extractor.extract(image),
                    check_unique=True
                )

        assert len(caught_warnings) == 1
        assert issubclass(caught_warnings[-1].category, UserWarning)
        assert str(
            caught_warnings[-1].message
        ) == 'Tensor being indexed already exists in ' + \
            'the database and the check for duplicates ' + \
            'are on. Refusing to store this tensor again.'


def test_open_index():
    """Unit test for index opening."""
    with Index(TEST_VECTOR_SIZE, TEST_INDEX_PATH) as index:
        assert index.size == TEST_VECTOR_SIZE


def test_context():
    """Unit test to test context opening and close."""
    with Index(TEST_VECTOR_SIZE, TEST_INDEX_PATH) as index:
        assert isinstance(index, Index)


def test_items():
    """Unit test for method items."""
    with Index(TEST_VECTOR_SIZE, TEST_INDEX_PATH) as index:
        all_items = list(index.items())
        for test_item, method_item in zip(all_items, index.items()):
            assert test_item == method_item


def test_values():
    """Unit test for method items."""
    with Index(TEST_VECTOR_SIZE, TEST_INDEX_PATH) as index:
        all_values = list(index.values())

        for test_value, method_value in zip(all_values, index.values()):
            assert test_value == method_value


def test_items_values():
    """Unit test for method items_values."""
    with Index(TEST_VECTOR_SIZE, TEST_INDEX_PATH) as index:
        all_values = list(index.values())
        all_items = list(index.items())
        for items_values, test_item, test_value in zip(
                index.items_values(), all_items, all_values
        ):
            method_item, method_value = items_values

            assert test_item == method_item and \
                test_value == method_value


def test_preprocessor_animated_gif():
    """Unit test for method preprocessor, animated GIF case."""
    with Extractors(
        Characteristics.HEAVYWEIGHT_SLOW_HUGE_PRECISION
    ) as extractors:
        assert extractors.preprocessor(TEST_ANIMATED_GIF).shape == \
            (1, 480, 480, 3)


def test___get_item__():
    """Unit test for magic method __getitem__."""
    with Index(TEST_VECTOR_SIZE, TEST_INDEX_PATH) as index:
        all_values = list(index.values())
        assert index[0] == all_values[0]


def test_reversed__get_item__():
    """Unit test for magic method __getitem__, reversed case."""
    with Index(TEST_VECTOR_SIZE, TEST_INDEX_PATH) as index:
        all_values = list(index.values())
        assert index[-1] == all_values[-1]


def test___len__():
    """Unit test for magic method __len__"""
    with Index(TEST_VECTOR_SIZE, TEST_INDEX_PATH) as index:
        all_items = list(index.items())
        assert len(index) == len(all_items)


def test___iter__():
    """Unit test for magic method __iter__"""
    with Index(TEST_VECTOR_SIZE, TEST_INDEX_PATH) as index:
        all_values = list(index.values())
        for test_value, method_value in zip(all_values, index):
            assert test_value == method_value


def test___next__():
    """Unit test for magic method __next__"""
    with Index(TEST_VECTOR_SIZE, TEST_INDEX_PATH) as index:
        all_values = list(index.values())
        for value in all_values:
            assert next(index) == value


def test_size():
    """Unit test for method size."""
    with Index(TEST_VECTOR_SIZE, TEST_INDEX_PATH) as index:
        assert index.size == TEST_VECTOR_SIZE


def test_path_property():
    """Unit test for path property."""
    with Index(TEST_VECTOR_SIZE, TEST_INDEX_PATH) as index:
        assert index.path == os.path.join(TEST_INDEX_PATH, index.index_name)


def test_trees_property():
    """Unit test for path property."""
    with Index(TEST_VECTOR_SIZE, TEST_INDEX_PATH) as index:
        assert index.trees == .01


def test_volatile_property():
    """Unit test for volatile property."""
    with Index(TEST_VECTOR_SIZE, TEST_INDEX_PATH) as index:
        assert not index.volatile


def test_trees_property_setter():
    """Unit test for path property."""
    with Index(TEST_VECTOR_SIZE, TEST_INDEX_PATH) as index:
        index.trees = 1

        assert index.trees == 1


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
    new_tensor = numpy.random.normal(size=TEST_VECTOR_SIZE)

    with Index(TEST_VECTOR_SIZE, TEST_INDEX_PATH) as index:
        test_size_before = len(index)

        index.append(new_tensor)

        test_size_after = len(index)

        assert test_size_after == test_size_before + 1

        numpy.testing.assert_array_almost_equal(
            index[-1], new_tensor, decimal=3
        )


def test_remove():
    """Unit test for method remove."""
    index_to_remove = 8

    def remove_routines(temp_dir):
        """Closure as helper for remove tests."""
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

    if system() == 'Windows':
        temp_dir = tempfile.TemporaryDirectory()

        remove_routines(temp_dir.name)

        temp_dir.cleanup()
    else:
        with tempfile.TemporaryDirectory() as temp_dir:
            remove_routines(temp_dir.name)


def test_pop():
    """Unit test for method pop."""
    if system() == 'Windows':
        temp_dir = tempfile.TemporaryDirectory()

        pop_routines(temp_dir.name)

        temp_dir.cleanup()
    else:
        with tempfile.TemporaryDirectory() as temp_dir:
            with Index(TEST_VECTOR_SIZE, data_dir=temp_dir.name) as index:
                for _ in range(16):
                    index.append(numpy.random.normal(size=TEST_VECTOR_SIZE))

                test_size_before = len(index)

                test_value_before = index[-1]

            with Index(TEST_VECTOR_SIZE, data_dir=temp_dir.name) as index:
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


def test_group_by():
    """Unit test for method group_by."""
    expected_result = {0: [25]}

    with Index(4, TEST_INDEX_SEARCH_PATH) as index:
        test_result = [*index.group_by(top=1)][0]

    assert expected_result == test_result


def test_group_by_position():
    """Unit test for method group_by."""
    expected_result = [25, 89, 88, 44, 38, 64, 10, 101, 78, 67]

    with Index(4, TEST_INDEX_SEARCH_PATH) as index:
        test_result = [*index.group_by(position=0)][0]

    assert expected_result == test_result


def test_export_group_by():
    """Unit test for method export_group_by method."""
    test_vector_size = 1024

    def export_routines(temp_dir, new_temp_dir):
        with Index(test_vector_size, data_dir=temp_dir) as index:
            test_search = PupylImageSearch(temp_dir)
            test_search.index(TEST_INDEX_EXPORT)

            index.export_by_group_by(new_temp_dir)

            assert os.path.exists(os.path.join(new_temp_dir, '0', '1.jpg'))
            assert os.path.exists(
                os.path.join(new_temp_dir, '0', 'group.jpg')
            )
            assert os.path.exists(os.path.join(new_temp_dir, '1', '1.jpg'))
            assert os.path.exists(
                os.path.join(new_temp_dir, '1', 'group.jpg')
            )

    # Windows: bypass clean up errors
    if system() == 'Windows':
        temp_dir = tempfile.TemporaryDirectory()
        new_temp_dir = tempfile.TemporaryDirectory()

        export_routines(temp_dir.name, new_temp_dir.name)

        temp_dir.clean_up()
        new_temp_dir.clean_up()
    else:
        with tempfile.TemporaryDirectory() as temp_dir, \
                tempfile.TemporaryDirectory() as new_temp_dir:
            export_routines(temp_dir.name, new_temp_dir.name)


def test_export_group_by_position():
    """Unit test for method export_group_by method, position case."""
    test_vector_size = 1024

    def export_routines(temp_dir, new_temp_dir):
        """Closure to support export routines test."""
        test_search = PupylImageSearch(temp_dir)
        test_search.index(TEST_INDEX_EXPORT)

        with Index(test_vector_size, data_dir=temp_dir) as index:
            index.export_by_group_by(new_temp_dir, position=1)

            assert os.path.exists(os.path.join(new_temp_dir, '1', '1.jpg'))
            assert os.path.exists(
                os.path.join(new_temp_dir, '1', 'group.jpg')
            )

    # Windows: bypass clean up errors
    if system() == 'Windows':
        temp_dir = tempfile.TemporaryDirectory()
        new_temp_dir = tempfile.TemporaryDirectory()

        export_routines(temp_dir.name, new_temp_dir.name)

        temp_dir.cleanup()
        new_temp_dir.cleanup()
    else:
        with tempfile.TemporaryDirectory() as temp_dir, \
                tempfile.TemporaryDirectory() as new_temp_dir:
            export_routines(temp_dir.name, new_temp_dir.name)


def test_export_results():
    """Unit test for method export_results."""
    test_vector_size = 1024

    def export_routines(temp_dir, new_temp_dir):
        """Closure to support export routines test."""
        test_search = PupylImageSearch(temp_dir)
        test_search.index(TEST_INDEX_EXPORT)

        with Index(test_vector_size, data_dir=temp_dir) as index:
            index.export_results(
                new_temp_dir, test_search.search(
                    os.path.join(TEST_INDEX_EXPORT, '1.jpg')
                ),
                keep_ids=True
            )

            assert os.path.exists(os.path.join(new_temp_dir, '1.jpg'))

            index.export_results(
                new_temp_dir, test_search.search(
                    os.path.join(TEST_INDEX_EXPORT, '1.jpg')
                ),
                keep_names=True
            )

            assert os.path.exists(os.path.join(new_temp_dir, '1.jpg'))

    # Windows: bypass clean up errors
    if system() == 'Windows':
        temp_dir = tempfile.TemporaryDirectory()
        new_temp_dir = tempfile.TemporaryDirectory()

        export_routines(temp_dir.name, new_temp_dir.name)
    else:
        with tempfile.TemporaryDirectory() as temp_dir, \
                tempfile.TemporaryDirectory() as new_temp_dir:
            export_routines(temp_dir.name, new_temp_dir.name)
