"""
Unit tests related to duplex.file_io module
"""
from os import walk
from os.path import abspath
from unittest import TestCase

from duplex.file_io import FileIO, Protocols
from duplex.exceptions import FileTypeNotSupportedYet


TEST_DIR = 'tests/'
TEST_SCAN_DIR = TEST_DIR + 'test_scan/'
TEST_UNKNOWN = 'unk://path'
TEST_UNSUPPORTED_FILE_TYPE = abspath(f'{TEST_DIR}not_image.txt')
TEST_LOCAL = abspath(f'{TEST_DIR}test_image.jpg')
TEST_URL = 'https://upload.wikimedia.org/wikipedia/commons/thumb/e/e4/' + \
    'Cheshm-Nazar.JPG/320px-Cheshm-Nazar.JPG'


class TestCases(TestCase):
    """
    Unit tests over special cases
    """
    def test__get_local_unsuccessful(self):
        """
        Unit test for _get_local method, local unsuccessful case
        """
        with self.assertRaises(IOError):
            FileIO._get_local(TEST_UNKNOWN)

    def test_infer_file_type_from_uri_unknown(self):
        """
        Unit test infer_file_type_from_uri, unknown case
        """
        with self.assertRaises(FileTypeNotSupportedYet):
            file_io = FileIO()

            file_io.infer_file_type_from_uri(TEST_UNKNOWN)

    def test_scan_unknown_file(self):
        """
        Unit test for scan method, unknown file case
        """
        with self.assertRaises(StopIteration):
            next(FileIO.scan(TEST_UNKNOWN))


def test__infer_protocol_http():
    """
    Unit tests for _infer_protocol method, http case
    """
    assert FileIO._infer_protocol(TEST_URL) is Protocols.HTTP


def test__infer_protocol_local():
    """
    Unit tests for _infer_protocol method, local case
    """
    assert FileIO._infer_protocol(TEST_LOCAL) is Protocols.FILE


def test__infer_protocol_unknown():
    """
    Unit tests for _infer_protocol method, unknown case
    """
    assert FileIO._infer_protocol(TEST_UNKNOWN) is Protocols.UNKNOWN


def test__get_url_successful():
    """
    Unit tests for _get_url method, successful case
    """
    assert isinstance(FileIO._get_url(TEST_URL), bytes)


def test__get_url_unsuccessful():
    """
    Unit tests for _get_url method, unsuccessful case
    """
    try:
        FileIO._get_url(TEST_UNKNOWN)
    except IOError:
        assert True


def test_get_http():
    """
    Unit test for get method, http case
    """
    assert isinstance(FileIO.get(TEST_URL), bytes)


def test_get_local():
    """
    Unit test for get method, http case
    """
    assert isinstance(FileIO.get(TEST_LOCAL), bytes)


def test__get_local_successful():
    """
    Unit test for _get_local method, local successful case
    """
    assert isinstance(FileIO._get_local(TEST_LOCAL), bytes)


def test_get_unknown():
    """
    Unit test for get method, unknown case
    """
    assert FileIO.get(TEST_UNKNOWN) is Protocols.UNKNOWN


def test_scan_file():
    """
    Unit test for scan method, file case
    """
    assert next(FileIO.scan(TEST_LOCAL)) == TEST_LOCAL


def test_scan_directory():
    """
    Unit test for scan method, directory case
    """
    test_against_tree = [
        abspath(f'{TEST_SCAN_DIR}{ffile}')
        for ffile in [*walk(TEST_SCAN_DIR)][0][-1]
    ]

    test_current_tree = [*FileIO.scan(TEST_SCAN_DIR)]

    assert test_current_tree == test_against_tree


def test_infer_file_type_from_uri_with_mimetype():
    """
    Unit test for method infer_file_type_from_uri,
    with mimetype case
    """
    file_io = FileIO()

    _, mime = file_io.infer_file_type_from_uri(
        TEST_LOCAL,
        mimetype=True
    )

    assert mime == 'image/jpeg'


def test_infer_file_type_from_uri_no_mimetype():
    """
    Unit test for method infer_file_type_from_uri,
    no mimetype case
    """
    file_io = FileIO()

    assert file_io.infer_file_type_from_uri(
        TEST_LOCAL,
        mimetype=False
    ) == 'JFI'


def test_infer_file_type_from_uri_unsupported():
    """
    Unit test for method infer_file_type_from_uri,
    unsupported file type case
    """
    file_io = FileIO()

    assert file_io.infer_file_type_from_uri(
        TEST_UNSUPPORTED_FILE_TYPE,
        mimetype=True
    ) == 'text/plain'


def test_infer_file_type_from_uri_remote():
    """
    Unit test for method infer_file_type_from_uri,
    remote case
    """
    file_io = FileIO()

    assert file_io.infer_file_type_from_uri(TEST_URL) == 'JPG'
