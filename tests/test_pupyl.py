"""Unit tests for main module pupyl."""
import os
import json
from tempfile import gettempdir, TemporaryDirectory
from unittest import TestCase
from urllib.error import URLError

from pupyl.search import PupylImageSearch
from pupyl.embeddings.features import Characteristics


TEST_DATA_DIR = os.path.join(gettempdir(), 'pupyl_tests/')
PUPYL = PupylImageSearch(data_dir=TEST_DATA_DIR, extreme_mode=True)
TEST_SCAN_DIR = os.path.abspath('tests/test_scan/test_csv.csv.gz')
TEST_INVALID_URL = os.path.abspath('tests/test_scan/invalid.csv')
TEST_QUERY_IMAGE = 'https://static.flickr.com/210/500863916_bdd4b8cc5a.jpg'
TEST_CONFIG_DIR = os.path.abspath('tests/test_index/')


class TestCases(TestCase):
    """Unit tests over special cases."""

    def test_index_invalid_url(self):
        """Unit test for method index, invalid url case."""
        with self.assertRaises(URLError):
            PUPYL.index(TEST_INVALID_URL)


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
            characteristic=Characteristics.LIGHTWEIGHT_REGULAR_PRECISION
        )

        assert pupyl_test._import_images and \
            pupyl_test._characteristic == Characteristics.\
            LIGHTWEIGHT_REGULAR_PRECISION


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


def test_search_returning_metadata():
    """Unit test for method search, returning image metadata case."""
    test_results = [*PUPYL.search(
        TEST_QUERY_IMAGE,
        top=1,
        return_metadata=True
    )][0]

    del test_results['original_access_time']

    assert test_results == {
        'id': 0,
        'original_file_name': '500863916_bdd4b8cc5a.jpg',
        'original_file_size': '25K',
        'original_path': 'https://static.flickr.com/210'}
