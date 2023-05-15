"""Unit tests related to duplex.file_io module."""
import os
import csv
import tempfile
import mimetypes
from os import walk
from pathlib import Path
from unittest import TestCase
from tarfile import is_tarfile
from urllib.error import URLError
from os.path import abspath, exists, join

from pupyl.duplex.file_io import FileIO, Protocols
from pupyl.duplex.file_types import TarCompressedTypes
from pupyl.duplex.exceptions import FileTypeNotSupportedYet, \
    FileScanNotPossible


TEST_DIR = 'tests/'
TEST_SCAN_DIR = TEST_DIR + 'test_scan/'
TEST_UNKNOWN = 'unk://path'
TEST_UNSUPPORTED_FILE_TYPE = abspath(f'{TEST_DIR}not_image.inv')
TEST_LOCAL = abspath(f'{TEST_DIR}test_image.jpg')
TEST_URL = 'https://upload.wikimedia.org/wikipedia/commons/' + \
    'thumb/e/e4/Cheshm-Nazar.JPG/320px-Cheshm-Nazar.JPG'
TEST_URL_NO_DATE = 'http://images.protopage.com/view/572714/' + \
    'axuvb8oxm7liskynxggfczfus.jpg'
TEST_URL_FORBIDDEN = 'https://cutt.ly/hWtd8dN'
TEST_URL_TIMEOUT = 'http://www.pedigree.com.sg/breeds/images/' + \
    'norwich_terr_02.jpg'
TEST_CSV = abspath(TEST_SCAN_DIR + 'test_csv.csv')
TEST_CSV_ZIP = abspath(TEST_SCAN_DIR + 'test_csv.csv.zip')
TEST_CSV_GZ = abspath(TEST_SCAN_DIR + 'test_csv.csv.gz')
TEST_CSV_BZ2 = abspath(TEST_SCAN_DIR + 'test_csv.csv.bz2')
TEST_CSV_XZ = abspath(TEST_SCAN_DIR + 'test_csv.csv.xz')
TEST_TAR_LOCATION = TEST_DIR + 'tar_files'


def util_test_csv(path):
    """
    Closure to mimic scan_csv behaviour.
    """
    with open(path) as ffile:
        reader = csv.reader(ffile)

        for row in reader:
            yield row[0]


class TestCases(TestCase):
    """Unit tests over special cases."""

    def test__get_local_unsuccessful(self):
        """Unit test for _get_local method, local unsuccessful case."""
        with self.assertRaises(IOError):
            FileIO._get_local(TEST_UNKNOWN)

    def test_infer_file_type_from_uri_unknown(self):
        """Unit test infer_file_type_from_uri, unknown case."""
        with self.assertRaises(FileTypeNotSupportedYet):
            file_io = FileIO()

            file_io.infer_file_type_from_uri(TEST_UNKNOWN)

    def test_scan_unknown_file(self):
        """Unit test for scan method, unknown file case."""
        file_io = FileIO()

        with self.assertRaises(FileTypeNotSupportedYet):
            next(file_io.scan(TEST_UNKNOWN))

    def test_scan_file(self):
        """Unit test for scan method, file case."""
        file_io = FileIO()

        with self.assertRaises(FileScanNotPossible):
            assert next(file_io.scan(TEST_LOCAL)) == TEST_LOCAL

    def test_scan_csv_unknown_file(self):
        """Unit test for scan_csv method, unknown file case."""
        file_io = FileIO()

        with self.assertRaises(FileTypeNotSupportedYet):
            next(file_io.scan_csv(TEST_UNKNOWN))

    def test_infer_file_type_from_uri_unsupported(self):
        """
        Unit test for method infer_file_type_from_uri,
        unsupported file type case.
        """
        file_io = FileIO()

        with self.assertRaises(FileTypeNotSupportedYet):
            file_io.infer_file_type_from_uri(
                TEST_UNSUPPORTED_FILE_TYPE,
                mimetype=True
            )

    def test__get_url_timeout(self):
        """Unit tests for _get_url method, timeout case."""
        with self.assertRaises(URLError):
            FileIO._get_url(TEST_URL_TIMEOUT)


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
    """Unit tests for _infer_protocol method, http case."""
    assert FileIO._infer_protocol(TEST_URL) is Protocols.HTTP


def test__infer_protocol_local():
    """Unit tests for _infer_protocol method, local case."""
    assert FileIO._infer_protocol(TEST_LOCAL) is Protocols.FILE


def test__infer_protocol_unknown():
    """Unit tests for _infer_protocol method, unknown case."""
    assert FileIO._infer_protocol(TEST_UNKNOWN) is Protocols.UNKNOWN


def test__get_url_successful():
    """Unit tests for _get_url method, successful case."""
    assert isinstance(FileIO._get_url(TEST_URL), bytes)


def test__get_url_unsuccessful():
    """Unit tests for _get_url method, unsuccessful case."""
    try:
        FileIO._get_url(TEST_UNKNOWN)
    except IOError:
        assert True


def test__get_url_large_file():
    """Unit test for method _get_url, large file case."""
    test_url_big_file = 'https://speed.hetzner.de/10GB.bin'

    assert FileIO._get_url(
        test_url_big_file,
        headers={'User-Agent': 'Mozilla/5.0'}
    ) == b''


def test__get_local_big_file():
    """Unit test for method _get_local, big file case."""
    with tempfile.NamedTemporaryFile() as temp_file:
        while int(
            os.path.getsize(temp_file.name) / (2 ** 30)
        ) < FileIO.max_file_size:
            temp_file.write(b'a' * (2 ** 16))

        assert FileIO._get_local(temp_file.name) == b''


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


def test_get_file_scheme():
    """Unit test for get method, file scheme case."""
    test_file = f'file:///{TEST_LOCAL}'

    assert isinstance(FileIO.get(test_file), bytes)


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
        assert method_row == util_row


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


def test_get_metadata_http():
    """Unit test for method get_metadata, http case."""
    test_metadata = {
        'original_file_name': '320px-Cheshm-Nazar.JPG',
        'original_path': """https://upload.wikimedia.org/wikipedia/commons/
        thumb/e/e4/Cheshm-Nazar.JPG""".replace('\n        ', ''),
        'original_file_size': '9K'
    }

    test_request_metadata = FileIO.get_metadata(TEST_URL)

    del test_request_metadata['original_access_time']

    assert test_metadata == test_request_metadata


def test_get_metadata_http_no_date():
    """Unit test for method get_metadata, http and not date case."""
    test_metadata = {
        'original_file_name': 'axuvb8oxm7liskynxggfczfus.jpg',
        'original_path': """http://images.protopage.com/view/
        572714""".replace('\n        ', '')
    }

    test_request_metadata = FileIO.get_metadata(TEST_URL_NO_DATE)

    del test_request_metadata['original_access_time']
    del test_request_metadata['original_file_size']

    assert test_metadata == test_request_metadata


def test_get_metadata_local():
    """Unit test for method get_metadata, local case."""
    test_metadata = {
        'original_file_name': 'test_image.jpg',
        'original_path': abspath('tests'),
        'original_file_size': '5K'
    }

    test_local_metadata = FileIO.get_metadata(TEST_LOCAL)

    del test_local_metadata['original_access_time']

    assert test_metadata == test_local_metadata


def test_timestamp_to_iso8601():
    """Unit test for method timestamp_to_iso8601"""
    test_timestamp = 1591123280
    expected_return = '2020-06-02T18:41:20'

    assert FileIO.timestamp_to_iso8601(test_timestamp) == expected_return


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


def test_infer_file_type_from_uri_remote():
    """
    Unit test for method infer_file_type_from_uri,
    remote case.
    """
    file_io = FileIO()

    assert file_io.infer_file_type_from_uri(TEST_URL) == 'JPG'


def test_infer_file_type_tar_files():
    """Unit test for method infer_file_type_from_uri, tar file case."""
    file_io = FileIO()

    for ffile in os.listdir(TEST_TAR_LOCATION):
        test_file_type = mimetypes.guess_type(
            os.path.join(
                TEST_TAR_LOCATION,
                ffile
            )
        )[1]

        assert file_io.infer_file_type_from_uri(
            os.path.join(
                TEST_TAR_LOCATION,
                ffile
            ),
            mimetype=True
        ) == TarCompressedTypes.mime(test_file_type)

        assert file_io.infer_file_type_from_uri(
            os.path.join(
                TEST_TAR_LOCATION,
                ffile
            ),
            mimetype=False
        ) == TarCompressedTypes.name(test_file_type)


def test_progress_not_precise():
    """Unit test for method progress, not precise case."""
    test_generator = range(10)
    test_unpacked = [*test_generator]

    test_result_generator = FileIO.progress(test_generator, precise=False)
    test_result_unpacked = FileIO.progress(test_unpacked, precise=False)

    for t_gen, r_gen in zip(test_generator, test_result_generator):
        assert t_gen == r_gen

    for t_unp, r_unp in zip(test_unpacked, test_result_unpacked):
        assert t_unp == r_unp


def test_progress_precise():
    """Unit test for method progress, not precise case."""

    def test_gen():
        """Closure to test functions which returns generators."""
        for value in range(10):
            yield value

    test_generator = range(10)
    test_unpacked = [*test_generator]

    test_result_generator = FileIO.progress(test_generator, precise=True)
    test_result_unpacked = FileIO.progress(test_unpacked, precise=True)
    test_result_func_gen = FileIO.progress(test_gen(), precise=True)

    for t_gen, r_gen in zip(test_generator, test_result_generator):
        assert t_gen == r_gen

    for t_unp, r_unp in zip(test_unpacked, test_result_unpacked):
        assert t_unp == r_unp

    for t_fgen, r_fgen in zip(test_generator, test_result_func_gen):
        assert t_fgen == r_fgen


def test_resolve_path_end():
    """Unit test for method test_resolve_path_end."""
    test_path_with_sep = '/just/a/test/path/'
    test_path_without_sep = '/just/a/test/path'

    expected_return = '/just/a/test/path'

    assert FileIO.resolve_path_end(test_path_with_sep) == expected_return
    assert FileIO.resolve_path_end(test_path_without_sep) == expected_return


def test_dump():
    """Unit test for method dump."""
    file_io = FileIO()

    file_io.dump(TEST_SCAN_DIR, tempfile.gettempdir())

    assert is_tarfile(
        os.path.join(
            tempfile.gettempdir(),
            '.'.join(
                (
                    os.path.basename(
                        file_io.resolve_path_end(TEST_SCAN_DIR)
                    ),
                    'pupyl'
                )
            )
        )
    )


def test_bind():
    """Unit test for method bind."""
    file_io = FileIO()

    file_io.dump(TEST_SCAN_DIR, tempfile.gettempdir())

    file_io.bind(
        os.path.join(
            tempfile.gettempdir(),
            '.'.join(
                (
                    os.path.basename(
                        file_io.resolve_path_end(TEST_SCAN_DIR)
                    ),
                    'pupyl'
                )
            )
        ),
        os.path.join(tempfile.gettempdir(), TEST_SCAN_DIR)
    )

    assert os.path.isdir(
        os.path.join(
            tempfile.gettempdir(),
            TEST_SCAN_DIR
        )
    )


def test_scan_tar_files():
    """Unit test for method scan, compressed tar file case."""
    file_io = FileIO()

    for ffile in os.listdir(TEST_TAR_LOCATION):
        for dfile in file_io.scan(
            os.path.join(TEST_TAR_LOCATION, ffile)
        ):
            assert os.path.exists(dfile)


def test_scan_compressed_tar_file_local():
    """Unit test for method scan_compressed_tar_file, local case."""
    test_tar_compressed_file_readers = {
        'TZ2': 'r:bz2',
        'TGZ': 'r:gz',
        'TXZ': 'r:xz'
    }

    file_io = FileIO()

    for ffile in os.listdir(TEST_TAR_LOCATION):
        test_file_type = mimetypes.guess_type(
            os.path.join(
                TEST_TAR_LOCATION,
                ffile
            )
        )[1]

        for dfile in file_io.scan_compressed_tar_file(
            os.path.join(TEST_TAR_LOCATION, ffile),
            test_tar_compressed_file_readers[
                TarCompressedTypes.name(test_file_type)
            ]
        ):
            assert os.path.exists(dfile)


def test_scan_compressed_tar_file_http():
    """Unit test for method scan_compressed_tar_file, http case."""
    test_uri = 'http://localhost:8888/images.tar.xz'
    test_file_reader = 'r|xz'

    file_io = FileIO()

    for ffile in file_io.scan_compressed_tar_file(test_uri, test_file_reader):
        assert os.path.exists(ffile)


def test_request_http_not_found():
    """Unit test for method _get_url, http 404 case."""
    test_uri = 'http://localhost:8888/notfound'

    assert FileIO._get_url(test_uri) == b''


def test__file_scheme_to_path():
    """Unit test for method _file_scheme_to_path."""
    test_uri = 'file:///path/to/a/test/file'

    assert FileIO._file_scheme_to_path(test_uri) == '/path/to/a/test/file'


def test__get_url_forbidden():
    """Unit test for method _get_url, HTTP 403 case."""
    assert isinstance(FileIO._get_url(TEST_URL_FORBIDDEN), bytes)
