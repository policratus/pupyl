"""Unit tests related to addendum.operators module."""
from pupyl.addendum.operators import intmul


TEST_VALUE = 123123
TEST_RESULT_ZERO_VALUE = 123
TEST_FACTOR = .001


def test_intmul_valid_case():
    """Unit test for method intmul, valid case."""
    assert TEST_VALUE << intmul >> TEST_FACTOR == 123


def test_intmul_below_zero_case():
    """Unit test for method intmul, below zero case."""
    assert TEST_RESULT_ZERO_VALUE << intmul >> TEST_FACTOR == 1
