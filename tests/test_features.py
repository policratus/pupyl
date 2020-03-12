"""
Unit tests related to embeddings.features modules
"""
from os.path import abspath
from enum import Enum, auto
from unittest import TestCase

from embeddings.features import Characteristics
from embeddings.features import Extractors
from embeddings.exceptions import UnknownCharacteristics


TEST_LOCAL = abspath('tests/test_image.jpg')


class TestCharacteristics(Enum):
    """
    Defines enumerators to test if all characteristics are described
    """
    LIGHTWEIGHT_REGULAR_PRECISION = auto()
    MEDIUMWEIGHT_GOOD_PRECISION = auto()
    HEAVYWEIGHT_HUGE_PRECISION = auto()


class TestCases(TestCase):
    """
    Unit tests over special cases
    """
    def test_unknown_network_instance(self):
        """
        Unit test for an unknown network characteristic
        """
        with self.assertRaises(UnknownCharacteristics):
            Extractors('UNKNOWN')


def test_characteristics():
    """
    Unit test for characteristics definition
    """
    for characteristic in TestCharacteristics._member_names_:
        assert characteristic in Characteristics._member_names_


def test_network_instance():
    """
    Unit test for network instantiation
    """
    for characteristic in Characteristics:
        extractor = Extractors(characteristic)

        assert extractor._infer_network()[1].name == extractor.network.name


def test_preprocessor():
    """
    Unit test for preprocessor method
    """
    for characteristic in Characteristics:
        extractor = Extractors(characteristic)

        assert extractor.preprocessor(abspath(TEST_LOCAL)).shape == \
            (1, *extractor.image_input_shape, 3)


def test_extract():
    """
    Unit test for extract method
    """
    for characteristic in Characteristics:
        extractor = Extractors(characteristic)

        assert extractor.extract(abspath(TEST_LOCAL)).shape == \
            (1, extractor.network.output_shape[1])
