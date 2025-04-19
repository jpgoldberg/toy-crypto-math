from typing import (
    Any,
    Iterator,
    Optional,
    Protocol,
    runtime_checkable,
    TYPE_CHECKING,
)

from . import utils
from math import isqrt

if TYPE_CHECKING:
    from bitarray import bitarray
    from bitarray.util import count_n, ba2int

else:
    try:
        from bitarray import bitarray
        from bitarray.util import count_n, ba2int
    except ImportError:

        def bitarray(*args, **kwargs) -> Any:  # type: ignore
            raise NotImplementedError("bitarray is not installed")

        def count_n(*args, **kwargs) -> int:  # type: ignore
            raise NotImplementedError("bitarray is not installed")

        def ba2int(*args, **kwargs) -> int:  # type: ignore
            raise NotImplementedError("bitarray is not installed")


@runtime_checkable
class Sievish(Protocol):
    """Methods available for all Sieve-like classes.

    This is primary of use for testing, where one might need to write
    functions that interact with any of the Sieve classes.
    This also would probably make more sense as an abstract class
    instead of a Protocol.
    """

    @classmethod
    def reset(cls) -> None:
        """Resets the class largest sieve created if such a thing exists.

        This is a no-op for classes that do not cache the largest sieve they
        have created.
        Even for classes for which this does something, this class method is
        useful only for testing and profiling.
        """
        ...

    @property
    def count(self) -> int:
        """The total number of primes in the sieve"""
        ...

    @property
    def n(self) -> int:
        """The size of the sieve, including composites.

        The number n such that the sieve contains all primes <= n.
        """
        ...

    def primes(self, start: int = 1) -> Iterator[int]:
        """Iterator of primes starting at start-th prime.

        The 1st prime is 2. There is no zeroth prime.

        :raises ValueError: if start < 1
        """
        ...

    def to01(self) -> str:
        """The sieve as a string of 0s and 1s.

        The output is to be read left to right. That is, it should begin with
        ``001101010001`` corresponding to primes [2, 3, 5, 7, 11]
        """
        ...

    def extend(self, n: int) -> None:
        """Extends the the current sieve.

        :param n: value that the sieve will contain primes up to and including.
        """
        ...

    def __int__(self) -> int:
        """Sieve as an integer with 1 bits representing primes.

        Most significant 1 bit represents the largest prime in the sieve.
        For example if s is a sieve of size 5, ``int(s)`` returns 44 which
        is equivalent to 0b101100.
        """
        ...

    @classmethod
    def from_size[S](cls: type[S], size: int) -> S:
        """Returns a new sieve of primes less than or equal to size."""
        ...


class Sieve(Sievish):
    """Sieve of Eratosthenes.

    The good parts of this implementation are lifted from the example provided
    with the `bitarray package <https://pypi.org/project/bitarray/>`_ source.

    This depends on `bitarray package <https://pypi.org/project/bitarray/>`_.
    """

    _base_sieve = bitarray("0011")

    @classmethod
    def from_size[S](cls, size: int) -> "Sieve":
        s: Sieve = Sieve(size)
        return s

    def extend(self, n: int) -> None:
        len_c = len(self._sieve)
        if n <= len_c:
            return

        len_e = n - len_c
        self._sieve.extend([True] * len_e)

        for i in range(2, isqrt(n) + 1):
            if self._sieve[i] is False:
                continue
            self._sieve[i * i :: i] = False

    @classmethod
    def reset(cls) -> None:
        pass

    def __init__(self, n: int) -> None:
        """Creates sieve covering the first n integers.

        :raises ValueError: if n < 2.
        """

        if n < 2:
            raise ValueError("n must be greater than 2")

        self._sieve = self._base_sieve
        self.extend(n)
        self._n = n

        self._count: int = self._sieve[:n].count()
        self._bitstring: Optional[str] = None

    @property
    def n(self) -> int:
        return self._n

    @property
    def array(self) -> bitarray:
        """The sieve as a bitarray."""
        return self._sieve[: self._n]

    @property
    def count(self) -> int:
        """The number of primes in the sieve."""
        return self._count

    def to01(self) -> str:
        if self._bitstring is None:
            self._bitstring = self._sieve[: self._n].to01()
            assert isinstance(self._bitstring, str)
        return self._bitstring

    def nth_prime(self, n: int) -> int:
        """Returns n-th prime.

        :raises ValueError: if n exceeds count.
        """

        if n > self._count:
            raise ValueError("n cannot exceed count")

        return count_n(self._sieve, n)

    def primes(self, start: int = 1) -> Iterator[int]:
        if start < 1:
            raise ValueError("Start must be >= 1")
        for n in range(start, self._count + 1):
            yield count_n(self._sieve, n) - 1

    def __int__(self) -> int:
        reversed = self._sieve.copy()[: self._n]
        reversed.reverse()
        return ba2int(reversed)

    # "Inherit" docstrings. Can't do properties
    from_size.__doc__ = Sievish.from_size.__doc__
    __int__.__doc__ = Sievish.__int__.__doc__
    from_size.__doc__ = Sievish.from_size.__doc__
    extend.__doc__ = Sievish.extend.__doc__
    primes.__doc__ = Sievish.primes.__doc__
    reset.__doc__ = Sievish.reset.__doc__
    to01.__doc__ = Sievish.to01.__doc__


class SetSieve(Sievish):
    """Sieve of Eratosthenes using a native python set

    This consumes an enormous amount of early in initialization,
    and a SetSieve object will contain a list of prime integers,
    so even after initialization is requires more memory than the
    the integer or bitarray sieves.
    """

    _base_sieve: list[int] = [2, 3]

    def extend(self, n: int) -> None:
        self._sieve: list[int]
        if n <= self.count:
            return

        largest_p = self._sieve[-1]
        if n <= largest_p:
            return

        # This is where the heavy memory consumption comes in.
        # Use numpy or bitarray for vast improvements in space
        # and time.
        sieve = set(p for p in self._sieve)
        sieve = sieve.union(set(range(largest_p + 1, n + 1)))

        # We go through what remains in the sieve in numeric order,
        # eliminating multiples of what we find.
        #
        # We only need to go up to and including the square root of n,
        # remove all non-primes above that square-root =< n.
        for p in range(2, isqrt(n) + 1):
            if p in sieve:
                # Because we are going through sieve in numeric order
                # we know that multiples of anything less than p have
                # already been removed, so p is prime.
                # Our job is to now remove multiples of p
                # higher up in the sieve.
                for m in range(p + p, n + 1, p):
                    sieve.discard(m)

        self._sieve = sorted(sieve)

    @classmethod
    def reset(cls) -> None:
        pass

    def __init__(self, n: int) -> None:
        """Returns sorted list primes n =< n

        A pure Python (memory hogging) Sieve of Eratosthenes.
        This consumes lots of memory, and is here only to
        illustrate the algorithm.
        """

        self._int_value: int | None = None

        self._n = n
        self._sieve = self._base_sieve.copy()
        self.extend(n)

    @classmethod
    def from_size[S](cls, size: int) -> "SetSieve":
        return SetSieve(size)

    @property
    def count(self) -> int:
        return len(self._sieve)

    def primes(self, start: int = 1) -> Iterator[int]:
        if start < 1:
            raise ValueError("Start must be >= 1")

        for n in range(start, self.count + 1):
            yield self._sieve[n - 1]

    def __int__(self) -> int:
        result = sum((int(2**p) for p in self._sieve))
        return result

    @property
    def n(self) -> int:
        return self._n

    def to01(self) -> str:
        return format(self.__int__(), "b")[::-1]

    from_size.__doc__ = Sievish.from_size.__doc__
    __int__.__doc__ = Sievish.__int__.__doc__
    from_size.__doc__ = Sievish.from_size.__doc__
    extend.__doc__ = Sievish.extend.__doc__
    primes.__doc__ = Sievish.primes.__doc__
    reset.__doc__ = Sievish.reset.__doc__
    to01.__doc__ = Sievish.to01.__doc__


class IntSieve(Sievish):
    """A pure Python (using a large int) Sieve of Eratosthenes."""

    _BASE_SIEVE: int = int("1100", 2)

    @classmethod
    def reset(cls) -> None:
        pass

    def __init__(self, n: int) -> None:
        """Creates sieve of primes <= n"""

        self._sieve: int = self._BASE_SIEVE
        self._n = self._BASE_SIEVE.bit_length()
        self.extend(n)

        self._count = self._sieve.bit_count()

    def extend(self, n: int) -> None:
        if n <= self._sieve.bit_length():
            return
        ones = (2 ** ((n - self._n) + 1)) - 1
        ones = ones << self._n
        self._sieve |= ones

        self._n = n
        # We only need to go up to and including the square root of n,
        # remove all non-primes above that square-root =< n.
        for p in range(2, isqrt(n) + 1):
            # if utils.get_bit(self._sieve, p):
            if (self._sieve & (1 << p)) >> p:
                # Because we are going through sieve in numeric order
                # we know that multiples of anything less than p have
                # already been removed, so p is prime.
                # Our job is to now remove multiples of p
                # higher up in the sieve.
                for m in range(p + p, n + 1, p):
                    # self._sieve = utils.set_bit(self._sieve, m, False)
                    self._sieve = self._sieve & ~(1 << m)

    @classmethod
    def from_size[S](cls, size: int) -> "IntSieve":
        return IntSieve(size)

    def to01(self) -> str:
        return format(self._sieve, "b")[::-1]

    def nth_prime(self, n: int) -> int:
        """Returns n-th prime.

        :raises ValueError: if n exceeds count.
        """

        if n > self.count:
            raise ValueError("n cannot exceed count")

        result = utils.bit_index(self._sieve, n)
        assert result is not None  # because we checked n earlier
        return result

    @property
    def count(self) -> int:
        return self._count

    @property
    def n(self) -> int:
        return self._n

    def primes(self, start: int = 1) -> Iterator[int]:
        if start < 1:
            raise ValueError("Start must be >= 1")
        for n in range(start, self.count + 1):
            pm = utils.bit_index(self._sieve, n)
            assert pm is not None
            yield pm

    def __int__(self) -> int:
        return self._sieve

    # 'Inherit' docstrings
    from_size.__doc__ = Sievish.from_size.__doc__
    __int__.__doc__ = Sievish.__int__.__doc__
    from_size.__doc__ = Sievish.from_size.__doc__
    extend.__doc__ = Sievish.extend.__doc__
    primes.__doc__ = Sievish.primes.__doc__
    reset.__doc__ = Sievish.reset.__doc__
    to01.__doc__ = Sievish.to01.__doc__
