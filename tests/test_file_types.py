"""
Unit tests related to duplex.image module
"""
import os
import mimetypes
from unittest import TestCase

from pupyl.duplex.file_types import FileType, TarCompressedTypes
from pupyl.duplex.exceptions import FileTypeNotSupportedYet


TEST_DIR = 'tests'
TEST_LOCAL = os.path.join(TEST_DIR, 'test_image.jpg')
TEST_UNKNOWN = os.path.join(TEST_DIR, 'compressed_image.npy')
TEST_TAR_LOCATION = os.path.join(TEST_DIR, 'tar_files')


class TestCases(TestCase):
    """
    Unit tests over special cases
    """

    def test_guess_file_type_unknown_case(self):
        """
        Unit test for guess_file_type method, file type
        unknown case
        """
        with self.assertRaises(FileTypeNotSupportedYet):
            with open(TEST_UNKNOWN, 'rb') as ffile:
                FileType.guess_file_type(ffile)


def test_guess_file_type_known_case():
    """
    Unit test for guess_file_type method, file type
    known case
    """
    with open(TEST_LOCAL, 'rb') as ffile:
        assert FileType.guess_file_type(ffile.read()) == 'JPG'


def test_tar_compressed_types_resolve():
    """Unit test for tar_compressed_types_resolve method"""
    for ffile in os.listdir(TEST_TAR_LOCATION):
        test_type = mimetypes.guess_type(
            os.path.join(TEST_TAR_LOCATION, ffile)
        )[1]

        assert FileType.tar_compressed_types_resolve(
            test_type,
            mimetype=False
        ) == TarCompressedTypes.name(test_type)

        assert FileType.tar_compressed_types_resolve(
            test_type,
            mimetype=True
        ) == TarCompressedTypes.mime(test_type)
