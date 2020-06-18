"""Unit tests for main module pupyl."""
import os
from tempfile import gettempdir
from pupyl import PupylImageSearch


TEST_DATA_DIR = os.path.join(gettempdir(), 'pupyl_tests/')
PUPYL = PupylImageSearch(data_dir=TEST_DATA_DIR)
TEST_SCAN_DIR = os.path.abspath('tests/test_scan/test_csv.csv.gz')
TEST_QUERY_IMAGE = 'https://static.flickr.com/210/500863916_bdd4b8cc5a.jpg'


def test_index():
    """Unit test for method index."""
    PUPYL.index(TEST_SCAN_DIR)

    assert os.path.isdir(TEST_DATA_DIR) and \
        os.path.isfile(os.path.join(TEST_DATA_DIR, 'pupyl.index')) and \
        os.path.isfile(os.path.join(TEST_DATA_DIR, '0', '0.jpg'))


def test_search():
    """Unit test for method search."""
    expected_results = [0]
    test_results = PUPYL.search(TEST_QUERY_IMAGE, top=1)

    assert [*test_results] == expected_results
