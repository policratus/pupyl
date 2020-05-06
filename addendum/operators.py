"""
operators Module.

Overloaded and new python operators.
"""


class Infix:
    """Definitions for infix operators."""

    def __init__(self, method):
        """Infix operators."""
        self.method = method

    def __rlshift__(self, other):
        """Supporting reversed right hand operations."""
        return Infix(lambda x, self=self, other=other: self.method(other, x))

    def __rshift__(self, other):
        """Supporting reversed right hand operations."""
        return self.method(other)


# intmul
# Performs an integer multiplication.
# If result is less than or equal to zero, it bounds to one.
#

intmul = Infix(lambda x, y: 1 if int(x * y) <= 0 else int(x * y))
