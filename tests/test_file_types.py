"""
Unit tests related to duplex.image module
"""
from os.path import abspath
from unittest import TestCase

from duplex.file_types import FileType
from duplex.exceptions import FileTypeNotSupportedYet


TEST_DIR = 'tests/'
TEST_LOCAL = abspath(f'{TEST_DIR}test_image.jpg')
TEST_UNKNOWN = abspath(f'{TEST_DIR}test.db')


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
        assert FileType.guess_file_type(ffile.read()) == 'JFI'
