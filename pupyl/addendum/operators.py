"""Overloaded and new python operators."""


class Infix:
    """Definitions for infix operators."""

    def __init__(self, method):
        """Defining infix operators, which is a way to overload
        (or create) new operators.

        Parameters
        ----------
        method: callable
            A function that will work as a new operator.

        Notes
        -----
        More about infix operators:
        https://www.geeksforgeeks.org/prefix-infix-conversion/
        """
        self.method = method

    def __rlshift__(self, other):
        """Supporting reversed right hand bitshift operations, in this case
        the leftmost operator.

        Parameters
        ----------
        other: callable
            The counterpart of operation.

        Example
        -------
        1 << 2
        """
        return Infix(lambda x, self=self, other=other: self.method(other, x))

    def __rshift__(self, other):
        """Supporting reversed right hand bitshift operations, in this case
        the rightmost operator.

        Parameters
        ----------
        other: callable
            The counterpart of operation.

        Example
        -------
        1 >> 2
        """
        return self.method(other)


# intmul
# Performs an integer multiplication.
# If result is less than or equal to zero, it bounds to one.

intmul = Infix(lambda x, y: 1 if int(x * y) <= 0 else int(x * y))
