"""
Unit tests related to embeddings.features modules
"""
from os.path import abspath
from enum import Enum, auto
from unittest import TestCase

from pupyl.embeddings.features import Characteristics, Extractors
from pupyl.embeddings.exceptions import UnknownCharacteristics


TEST_LOCAL = abspath('tests/test_image.jpg')
UNKNOWN_CHARACTERISTICS = 'UNKNOWN'


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
        """Unit test for an unknown network characteristic."""
        with self.assertRaises(UnknownCharacteristics):
            Extractors(UNKNOWN_CHARACTERISTICS)

    def test_unknown_characteristic(self):
        """Unit test for an unknown characteristic key."""
        with self.assertRaises(KeyError):
            _ = Characteristics[UNKNOWN_CHARACTERISTICS]


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
        with Extractors(characteristic) as extractor:
            assert extractor._infer_network()[1].name == extractor.network.name


def test_extractors_context_manager():
    """
    Unit test for context manager Extractors
    """
    for characteristic in Characteristics:
        with Extractors(characteristic) as extractors:
            assert isinstance(extractors, Extractors)


def test_preprocessor():
    """
    Unit test for preprocessor method
    """
    for characteristic in Characteristics:
        with Extractors(characteristic) as extractor:
            assert extractor.preprocessor(abspath(TEST_LOCAL)).shape == \
                (1, *extractor.image_input_shape, 3)


def test_extract():
    """
    Unit test for extract method
    """
    for characteristic in Characteristics:
        with Extractors(characteristic) as extractor:
            assert extractor.extract(abspath(TEST_LOCAL)).shape[0] == \
                extractor.network.output_shape[1]


def test_acceleration_discovery(monkeypatch):
    """
    Unit test for acceleration_discovery staticmethod
    """
    @staticmethod
    def mocked___init__(characteristics):
        """
        Closure to mock __init__ behaviour
        """
        del characteristics

    @staticmethod
    def mocked_acceleration_discovery():
        """
        Closure to mock acceleration_discovery behaviour
        """
        return True

    monkeypatch.setattr(
        Extractors,
        '__init__',
        mocked___init__
    )

    monkeypatch.setattr(
        Extractors,
        'acceleration_discovery',
        mocked_acceleration_discovery
    )

    assert Extractors(
        Characteristics.LIGHTWEIGHT_REGULAR_PRECISION
    ).acceleration_discovery()


def test_output_shape_property():
    """Unit test for property output_shape."""
    for characteristic in Characteristics:
        with Extractors(characteristic) as extractor:
            assert extractor.output_shape == extractor._features_output_shape
