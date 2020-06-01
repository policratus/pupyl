"""
Unit tests related to duplex.file_io module
"""
import csv
import tempfile
from os import walk
from os.path import abspath, exists, join
from pathlib import Path
from unittest import TestCase

from duplex.file_io import FileIO, Protocols
from duplex.exceptions import FileTypeNotSupportedYet, FileScanNotPossible


TEST_DIR = 'tests/'
TEST_SCAN_DIR = TEST_DIR + 'test_scan/'
TEST_UNKNOWN = 'unk://path'
TEST_UNSUPPORTED_FILE_TYPE = abspath(f'{TEST_DIR}not_image.txt')
TEST_LOCAL = abspath(f'{TEST_DIR}test_image.jpg')
TEST_URL = 'https://upload.wikimedia.org/wikipedia/commons/thumb/e/e4/' + \
    'Cheshm-Nazar.JPG/320px-Cheshm-Nazar.JPG'

TEST_CSV = abspath(TEST_SCAN_DIR + 'test_csv.csv')
TEST_CSV_ZIP = abspath(TEST_SCAN_DIR + 'test_csv.csv.zip')
TEST_CSV_GZ = abspath(TEST_SCAN_DIR + 'test_csv.csv.gz')
TEST_CSV_BZ2 = abspath(TEST_SCAN_DIR + 'test_csv.csv.bz2')
TEST_CSV_XZ = abspath(TEST_SCAN_DIR + 'test_csv.csv.xz')


def util_test_csv(path):
    """
    Closure to mimic scan_csv behaviour.
    """
    with open(path) as ffile:
        reader = csv.reader(ffile)

        for row in reader:
            yield row[0]


class TestCases(TestCase):
    """ Unit tests over special cases. """

    def test__get_local_unsuccessful(self):
        """ Unit test for _get_local method, local unsuccessful case. """
        with self.assertRaises(IOError):
            FileIO._get_local(TEST_UNKNOWN)

    def test_infer_file_type_from_uri_unknown(self):
        """ Unit test infer_file_type_from_uri, unknown case. """
        with self.assertRaises(FileTypeNotSupportedYet):
            file_io = FileIO()

            file_io.infer_file_type_from_uri(TEST_UNKNOWN)

    def test_scan_unknown_file(self):
        """
        Unit test for scan method, unknown file case
        """
        file_io = FileIO()

        with self.assertRaises(FileTypeNotSupportedYet):
            next(file_io.scan(TEST_UNKNOWN))

    def test_scan_file(self):
        """ Unit test for scan method, file case."""
        file_io = FileIO()

        with self.assertRaises(FileScanNotPossible):
            assert next(file_io.scan(TEST_LOCAL)) == TEST_LOCAL

    def test_scan_csv_unknown_file(self):
        """ Unit test for scan_csv method, unknown file case. """
        file_io = FileIO()

        with self.assertRaises(FileTypeNotSupportedYet):
            next(file_io.scan_csv(TEST_UNKNOWN))


def test_safe_temp_file():
    """Unit test for method safe_temp_file."""
    test_temp_file_name = FileIO.safe_temp_file()

    assert not exists(test_temp_file_name)


def test_safe_temp_file_exists():
    """Unit test for method safe_temp_file, file exists case."""
    test_temp_file_name = 'just_a_temp_file.txt'

    Path(join(tempfile.gettempdir(), test_temp_file_name)).touch()

    _ = FileIO.safe_temp_file(file_name=test_temp_file_name)

    assert not exists(test_temp_file_name)


def test__infer_protocol_http():
    """ Unit tests for _infer_protocol method, http case. """
    assert FileIO._infer_protocol(TEST_URL) is Protocols.HTTP


def test__infer_protocol_local():
    """ Unit tests for _infer_protocol method, local case. """
    assert FileIO._infer_protocol(TEST_LOCAL) is Protocols.FILE


def test__infer_protocol_unknown():
    """
    Unit tests for _infer_protocol method, unknown case.
    """
    assert FileIO._infer_protocol(TEST_UNKNOWN) is Protocols.UNKNOWN


def test__get_url_successful():
    """
    Unit tests for _get_url method, successful case.
    """
    assert isinstance(FileIO._get_url(TEST_URL), bytes)


def test__get_url_unsuccessful():
    """
    Unit tests for _get_url method, unsuccessful case.
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


def test_scan_directory():
    """
    Unit test for scan method, directory case
    """
    file_io = FileIO()

    test_against_tree = [
        abspath(f'{TEST_SCAN_DIR}{ffile}')
        for ffile in [*walk(TEST_SCAN_DIR)][0][-1]
        ]

    test_current_tree = [*file_io.scan(abspath(TEST_SCAN_DIR))]

    assert test_current_tree == test_against_tree


def test_scan_csv():
    """ Unit test for scan method, txt or csv case. """

    file_io = FileIO()

    for method_row, util_row in zip(file_io.scan(TEST_CSV),
                                    util_test_csv(TEST_CSV)):
        assert method_row[0] == util_row


def test_scan_scan_gzip():
    """ Unit test for scan method, gzip case. """
    file_io = FileIO()

    for method_row, util_row in zip(file_io.scan(TEST_CSV_GZ),
                                    util_test_csv(TEST_CSV)):
        assert method_row == util_row


def test_scan_scan_zip():
    """ Unit test for scan method, zip case. """
    file_io = FileIO()

    for method_row, util_row in zip(file_io.scan(TEST_CSV_ZIP),
                                    util_test_csv(TEST_CSV)):
        assert method_row == util_row


def test_scan_scan_bzip2():
    """ Unit test for scan method, gzip case. """
    file_io = FileIO()

    for method_row, util_row in zip(file_io.scan(TEST_CSV_BZ2),
                                    util_test_csv(TEST_CSV)):
        assert method_row == util_row


def test_scan_scan_xz():
    """ Unit test for scan method, lzma case. """
    file_io = FileIO()

    for method_row, util_row in zip(file_io.scan(TEST_CSV_XZ),
                                    util_test_csv(TEST_CSV)):
        assert method_row == util_row


def test_scan_csv_gzip():
    """ Unit test for scan_csv_gzip method. """
    for method_row, util_row in zip(FileIO.scan_csv_gzip(TEST_CSV_GZ),
                                    util_test_csv(TEST_CSV)):
        assert method_row == util_row


def test_scan_csv_xz():
    """ Unit test for scan_csv_xz method. """
    for method_row, util_row in zip(FileIO.scan_csv_xz(TEST_CSV_XZ),
                                    util_test_csv(TEST_CSV)):
        assert method_row == util_row


def test_scan_csv_zip():
    """ Unit test for scan_csv_zip method. """
    for method_row, util_row in zip(FileIO.scan_csv_zip(TEST_CSV_ZIP),
                                    util_test_csv(TEST_CSV)):
        assert method_row == util_row


def test_scan_csv_bzip2():
    """ Unit test for scan_csv_bzip2 method. """
    for method_row, util_row in zip(FileIO.scan_csv_bzip2(TEST_CSV_BZ2),
                                    util_test_csv(TEST_CSV)):
        assert method_row == util_row


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
        ) == 'JPG'


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
    remote case.
    """
    file_io = FileIO()

    assert file_io.infer_file_type_from_uri(TEST_URL) == 'JPG'
