"""Unit tests for main module pupyl."""
import os
import json
from unittest import TestCase
from urllib.error import URLError
from tempfile import gettempdir, TemporaryDirectory

from pupyl.indexer.facets import Index
from pupyl.search import PupylImageSearch
from pupyl.duplex.exceptions import FileIsNotImage
from pupyl.embeddings.features import Extractors, Characteristics


TEST_DATA_DIR = os.path.join(gettempdir(), 'pupyl_tests/')
PUPYL = PupylImageSearch(data_dir=TEST_DATA_DIR, extreme_mode=True)
TEST_SCAN_DIR = os.path.abspath('tests/test_scan/test_csv.csv.gz')
TEST_INVALID_URL = os.path.abspath('tests/test_scan/invalid.csv')
TEST_QUERY_IMAGE = 'https://static.flickr.com/210/500863916_bdd4b8cc5a.jpg'
TEST_INDEX_INVALID = os.path.abspath('tests/test_index_invalid')
TEST_CONFIG_DIR = os.path.abspath('tests/test_index/')


class TestCases(TestCase):
    """Unit tests over special cases."""

    def test_index_invalid_url(self):
        """Unit test for method index, invalid url case."""
        with self.assertRaises(URLError):
            PUPYL.index(TEST_INVALID_URL)

    def test_index_gaps(self):
        """Unit test for method index, gaps in images case."""
        with self.assertRaises(FileIsNotImage):
            with TemporaryDirectory() as temp_dir:
                pupyl_index_gaps = PupylImageSearch(data_dir=temp_dir)
                pupyl_index_gaps.index(TEST_INDEX_INVALID)


def test_index_no_config_file():
    """
    Unit test for PupylImageSearch class initialization,
    without configuration file case.
    """
    with TemporaryDirectory() as temp_dir:
        test_config = PupylImageSearch(data_dir=temp_dir).\
            _index_configuration('r')

        assert not test_config


def test_index_creation_chosen_parameters():
    """
    Unit test for PupylImageSearch class initialization,
    with chosen parameters case.
    """
    with TemporaryDirectory() as temp_dir:
        pupyl_test = PupylImageSearch(
            data_dir=temp_dir,
            import_images=True,
            characteristic=Characteristics.MINIMUMWEIGHT_FAST_SMALL_PRECISION
        )

        assert pupyl_test._import_images and \
            pupyl_test._characteristic == Characteristics.\
            MINIMUMWEIGHT_FAST_SMALL_PRECISION


def test_index_config_file():
    """Unit test for index creation, with config. file case."""
    test_config_file = 'index.json'

    with open(
        os.path.join(TEST_CONFIG_DIR, test_config_file)
    ) as config:
        configurations = json.load(config)

    test_pupyl = PupylImageSearch(TEST_CONFIG_DIR, extreme_mode=False)

    assert configurations['import_images'] == \
        test_pupyl._import_images

    assert configurations['characteristic'] == \
        test_pupyl._characteristic.name


def test_index():
    """Unit test for method index."""
    PUPYL.index(TEST_SCAN_DIR)

    assert os.path.isdir(TEST_DATA_DIR) and \
        os.path.isfile(os.path.join(TEST_DATA_DIR, 'pupyl.index')) and \
        os.path.isfile(os.path.join(TEST_DATA_DIR, '0', '0.jpg'))


def test_characteristic_by_name():
    """Unit test for instantiating a characteristic by its name."""
    test_characteristic = 'MEDIUMWEIGHT_QUICK_GOOD_PRECISION'

    with TemporaryDirectory() as temp_dir:
        test_pupyl = PupylImageSearch(
            data_dir=temp_dir,
            characteristic=test_characteristic
        )

        assert test_pupyl._characteristic.name == test_characteristic


def test_characteristic_by_value():
    """Unit test for instantiating a characteristic by its value."""
    # LIGHTWEIGHT_QUICK_SHORT_PRECISION
    test_characteristic = 4

    with TemporaryDirectory() as temp_dir:
        test_pupyl = PupylImageSearch(
            data_dir=temp_dir,
            characteristic=test_characteristic
        )

        assert test_pupyl._characteristic.value == test_characteristic


def test_index_no_extreme_mode():
    """Unit test for method index, non extreme mode case."""
    pupyl_non_extreme = PupylImageSearch(
        data_dir=TEST_DATA_DIR,
        extreme_mode=False
    )
    pupyl_non_extreme.index(TEST_SCAN_DIR)

    assert os.path.isdir(TEST_DATA_DIR) and \
        os.path.isfile(os.path.join(TEST_DATA_DIR, 'pupyl.index')) and \
        os.path.isfile(os.path.join(TEST_DATA_DIR, '0', '0.jpg'))


def test_pupyl_temp_data_dir():
    """Unit test for instance saving on temporary dir."""
    pupyl_test = PupylImageSearch()

    assert isinstance(pupyl_test, PupylImageSearch)


def test_search():
    """Unit test for method search."""
    expected_length_results = 1

    test_results = PUPYL.search(
        TEST_QUERY_IMAGE,
        top=expected_length_results
    )

    assert len([*test_results]) == expected_length_results


def test_search_distances():
    """Unit test for method search, returning distances case."""
    expected_result_index = 0
    expected_result_distance = .1

    test_results = PUPYL.search(
        TEST_QUERY_IMAGE,
        top=1,
        return_distances=True
    )

    test_results = [*test_results][0]
    test_results_index = test_results[0]
    test_results_distance = round(test_results[1], 1)

    assert test_results_index == expected_result_index
    assert test_results_distance == expected_result_distance


def test_search_non_extreme_mode():
    """Unit test for method search, non-extreme mode case."""
    expected_length_results = 1

    pupyl_non_extreme = PupylImageSearch(
        data_dir=TEST_DATA_DIR,
        extreme_mode=False
    )

    test_results = pupyl_non_extreme.search(
        TEST_QUERY_IMAGE,
        top=expected_length_results
    )

    assert len([*test_results]) == expected_length_results


def test_search_non_extreme_mode_distances():
    """Unit test for method search, non-extreme mode and distances ase."""
    expected_result_index = 0
    expected_result_distance = .1

    pupyl_non_extreme = PupylImageSearch(
        data_dir=TEST_DATA_DIR,
        extreme_mode=False
    )

    test_results = pupyl_non_extreme.search(
        TEST_QUERY_IMAGE,
        top=1,
        return_distances=True,
        return_metadata=False
    )

    test_results = [*test_results][0]
    test_results_index = test_results[0]
    test_results_distance = round(test_results[1], 1)

    assert test_results_index == expected_result_index
    assert test_results_distance == expected_result_distance


def test_search_returning_metadata():
    """Unit test for method search, returning image metadata case."""
    with TemporaryDirectory() as temp_dir:
        test_pupyl = PupylImageSearch(temp_dir)
        test_pupyl.index(TEST_SCAN_DIR)

        test_results = [*test_pupyl.search(
            TEST_QUERY_IMAGE,
            top=1,
            return_metadata=True
        )][0]

        del test_results['original_access_time']

        assert isinstance(test_results, dict)


def test_remove():
    """Unit test for method remove."""
    index_to_remove = 0

    with TemporaryDirectory() as temp_dir:
        test_pupyl = PupylImageSearch(temp_dir)

        test_pupyl.index(TEST_SCAN_DIR)

        print([*os.listdir(os.path.join(temp_dir, '0'))])

        length_indexer_before = len(test_pupyl.indexer)
        length_image_database_before = len(test_pupyl.image_database)

        test_pupyl.remove(index_to_remove)

        length_indexer_after = len(test_pupyl.indexer)
        length_image_database_after = len(test_pupyl.image_database)

        assert length_indexer_after == length_indexer_before - 1
        assert length_image_database_after == length_image_database_before - 1


def test_remove_non_extreme():
    """Unit test for method remove, non extreme mode."""
    index_to_remove = 0

    with TemporaryDirectory() as temp_dir:
        pupyl_non_extreme = PupylImageSearch(
            data_dir=temp_dir,
            extreme_mode=False,
            characteristic=Characteristics.HEAVYWEIGHT_SLOW_GOOD_PRECISION
        )

        pupyl_non_extreme.index(TEST_SCAN_DIR)

        with Extractors(
            characteristics=Characteristics.HEAVYWEIGHT_SLOW_HUGE_PRECISION,
            extreme_mode=False
        ) as extractor:
            with Index(extractor.output_shape, data_dir=temp_dir) as indexer:
                length_indexer_before = len(indexer)
                length_image_database_before = len(
                    pupyl_non_extreme.image_database
                )

        pupyl_non_extreme.remove(index_to_remove)

        with Extractors(
            characteristics=Characteristics.HEAVYWEIGHT_SLOW_HUGE_PRECISION,
            extreme_mode=False
        ) as extractor:
            with Index(extractor.output_shape, data_dir=temp_dir) as indexer:
                length_indexer_after = len(indexer)
                length_image_database_after = len(
                    pupyl_non_extreme.image_database
                )

    assert length_image_database_after == \
        length_image_database_before - 1
    assert length_indexer_after == length_indexer_before - 1
