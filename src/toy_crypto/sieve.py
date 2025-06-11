from functools import cache
import threading
from typing import (
    Any,
    Iterator,
    Protocol,
    Self,
    runtime_checkable,
    TYPE_CHECKING,
)

from . import bit_utils
from math import isqrt


_has_bitarry = True
if TYPE_CHECKING:
    from bitarray import bitarray
    from bitarray.util import count_n, ba2int

else:
    try:
        from bitarray import bitarray
        from bitarray.util import count_n, ba2int
    except ImportError:
        _has_bitarry = False

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

    _data: bitarray | list[int] | int

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

    def nth_prime(self, n: int) -> int:
        """Returns n-th prime.

        :raises ValueError: if n exceeds count.
        :raises ValueError: n < 1
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

    @classmethod
    def from_int[S](cls: type[S], n: int) -> S:
        """Returns a new sieve of primes from the bits of n."""
        ...

    @classmethod
    def from_list[S](
        cls: type[S], primes: list[int], size: int | None = None
    ) -> S:
        """Returns a new sieve of primes from list.

        If size is not specified it will be set to the largest value in primes

        :raises ValueError: if primes is empty
        """
        ...

    @classmethod
    def from_sieve[S: Sievish](cls: type[S], sieve: S, size: int | None) -> S:
        """New instance using already computed data in sieve.

        If size is not specified, new instance will be the same size as sieve.
        """
        if size is None:
            size = sieve.n

        if size < 2:
            raise ValueError("size must be greater than 2")

        instance = cls.__init__(sieve._data)  # type: ignore
        assert isinstance(instance, Sievish)
        instance._extend(size)
        instance._n = size

        return instance


class BaSieve(Sievish):
    """Sieve of Eratosthenes.

    The good parts of this implementation are lifted from the example provided
    with the `bitarray package <https://pypi.org/project/bitarray/>`_ source.

    This depends on `bitarray package <https://pypi.org/project/bitarray/>`_.
    """

    _base_sieve = bitarray("0011")

    _common_data = bitarray("0011")
    _largest_n: int = 2
    """These will be shared by all instances."""

    lock = threading.Lock()

    @classmethod
    def _extend(cls, n: int) -> None:
        if n <= cls._largest_n:
            return

        with cls.lock:
            len_e = n - cls._largest_n
            cls._common_data.extend([True] * len_e)

            """start is the multiple of the prime we start zeroing the
            array from. Typically that would be 2p, but we want to consider
            cases where the common_data is larger than n. All composites
            through largest largest_n have already been set to 0 in the array.

            So ``start`` must meet four conditions
            1. It must be a multiple of p
            2. It must be larger than p
            3. It must be larger than largest_n
            4. It must be the smallest number meeting the above conditions
            """

            start: int
            for p in range(2, isqrt(n) + 1):
                if cls._common_data[p]:
                    start = max(p + p, p * (p // cls._largest_n + 1))
                    cls._common_data[start::p] = 0
            cls._largest_n = n

    @classmethod
    def reset(cls) -> None:
        cls._common_data = cls._base_sieve.copy()
        cls._largest_n = 2

    @classmethod
    def from_int(cls, n: int) -> Self:
        instance = cls.__new__(cls)
        instance._n = n.bit_length()
        instance._data = bitarray(instance._n + 1)
        idx = 0
        while n:
            n, r = divmod(n, 2)
            instance._data[idx] = r
            idx += 1

        instance._count = instance._data.count()

        return instance

    @classmethod
    def from_size(cls, size: int) -> Self:
        if size < 2:
            raise ValueError("size must be greater than 2")

        instance = cls.__new__(cls)

        instance._extend(size)
        instance._n = size

        instance._count = instance._common_data[:size].count()

        return instance

    @classmethod
    def from_list(cls, primes: list[int], size: int | None = None) -> Self:
        if not primes:
            raise ValueError("primes cannot be empty")
        max_prime = max(primes)
        assert isinstance(max_prime, int)

        if size is None:
            size = max_prime

        instance = cls.__new__(cls)
        if max_prime > cls._largest_n:
            with cls.lock:
                extend_by = max_prime - cls._largest_n
                cls._common_data.extend([0] * extend_by)

                for p in primes:
                    if p > cls._largest_n:
                        instance._common_data[p] = 1
                cls._largest_n = max(size, max_prime)
        instance._n = size
        instance._count = instance._common_data[:size].count()

        return instance

    def __init__(self, data: bitarray, size: int | None) -> None:
        """Sieve from bitarray, treated as up to size.

        :raises ValueError: if size > len(data)
        """

        if size is None:
            size = len(data)

        if size > len(data):
            raise ValueError(
                "size cannot be larger than the length of the data"
            )
        if size > self._largest_n:
            with self.lock:
                self._largest_n = len(data)
                self._common_data = data

        self._n = size

        self._count: int = self._common_data[: self._n].count()

    @property
    def n(self) -> int:
        return self._n

    @property
    def count(self) -> int:
        """The number of primes in the sieve."""
        return self._count

    @cache
    def nth_prime(self, n: int) -> int:
        assert isinstance(self._common_data, bitarray)
        if n < 1:
            raise ValueError("n must be greater than zero")

        if n > self._count:
            raise ValueError("n cannot exceed count")

        return count_n(self._common_data, n)

    def primes(self, start: int = 1) -> Iterator[int]:
        if start < 1:
            raise ValueError("Start must be >= 1")
        for n in range(start, self._count + 1):
            yield count_n(self._common_data, n) - 1

    def __int__(self) -> int:
        reversed = self._common_data.copy()[: self._n]
        reversed.reverse()
        return ba2int(reversed)

    # "Inherit" docstrings. Can't do properties
    from_size.__doc__ = Sievish.from_size.__doc__
    __int__.__doc__ = Sievish.__int__.__doc__
    primes.__doc__ = Sievish.primes.__doc__
    reset.__doc__ = Sievish.reset.__doc__
    nth_prime.__doc__ = Sievish.nth_prime.__doc__
    from_int.__doc__ = Sievish.from_int.__doc__
    from_list.__doc__ = Sievish.from_list.__doc__


class SetSieve(Sievish):
    """Sieve of Eratosthenes using a native python set

    This consumes an enormous amount of early in initialization,
    and a SetSieve object will contain a list of prime integers,
    so even after initialization is requires more memory than the
    the integer or bitarray sieves.
    """

    _base_sieve: list[int] = [2, 3]

    def _extend(self, n: int) -> None:
        self._data: list[int]
        largest_p = self._data[-1]
        if n <= largest_p:
            return

        # This is where the heavy memory consumption comes in.
        # Use numpy or bitarray for vast improvements in space
        # and time.
        sieve = set(p for p in self._data)
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

        # sets, unlike dicts, are not guaranteed to preserve insertion order
        self._data = sorted(sieve)

    @classmethod
    def reset(cls) -> None:
        pass

    @classmethod
    def from_int(cls, n: int) -> Self:
        sieve = cls.__new__(cls)
        sieve._n = n.bit_length()
        sieve._data = list()

        for idx, bit in enumerate(bit_utils.bits(n)):
            if bit:
                sieve._data.append(idx)

        return sieve

    @classmethod
    def from_list(cls, primes: list[int], size: int | None = None) -> Self:
        if not primes:
            raise ValueError("primes cannot be empty")
        max_prime = max(primes)
        assert isinstance(max_prime, int)

        if size is None:
            size = max_prime

        instance = cls.__new__(cls)
        instance._data = sorted(primes)
        instance._n = size

        return instance

    def __init__(self, data: list[int]) -> None:
        """Returns sorted list primes n =< n

        A pure Python (memory hogging) Sieve of Eratosthenes.
        This consumes lots of memory, and is here only to
        illustrate the algorithm.
        """

        self._n = max(data)
        self._data = data  # type: ignore

    @classmethod
    def from_size[S](cls, size: int) -> "SetSieve":
        if size < 2:
            raise ValueError("size must be greater than 2")

        instance = cls.__new__(cls)

        instance._n = size
        instance._data = instance._base_sieve.copy()
        instance._extend(size)

        return instance

    @property
    def count(self) -> int:
        return len(self._data)

    def primes(self, start: int = 1) -> Iterator[int]:
        if start < 1:
            raise ValueError("Start must be >= 1")

        for n in range(start, self.count + 1):
            yield self._data[n - 1]

    def nth_prime(self, n: int) -> int:
        """Returns n-th prime. ``nth_prime(1) == 2``. There is no zeroth prime.

        :raises ValueError: if n exceeds count.
        :raises ValueError: n < 1
        """

        if n < 1:
            raise ValueError("n must be greater than zero")

        if n > self.count:
            raise ValueError("n cannot exceed count")

        return self._data[n - 1]

    def __int__(self) -> int:
        result = sum((int(2**p) for p in self._data))
        return result

    @property
    def n(self) -> int:
        return self._n

    from_size.__doc__ = Sievish.from_size.__doc__
    __int__.__doc__ = Sievish.__int__.__doc__
    primes.__doc__ = Sievish.primes.__doc__
    reset.__doc__ = Sievish.reset.__doc__
    nth_prime.__doc__ = Sievish.nth_prime.__doc__
    from_int.__doc__ = Sievish.from_int.__doc__
    from_list.__doc__ = Sievish.from_list.__doc__


class IntSieve(Sievish):
    """A pure Python (using a large int) Sieve of Eratosthenes."""

    _BASE_SIEVE: int = int("1100", 2)

    @classmethod
    def reset(cls) -> None:
        pass

    @classmethod
    def from_int(cls, n: int) -> Self:
        sieve = cls.__new__(cls)
        sieve._n = n.bit_length()
        sieve._data = n
        sieve._count = sieve._data.bit_count()

        return sieve

    @classmethod
    def from_list(cls, primes: list[int], size: int | None = None) -> Self:
        if not primes:
            raise ValueError("primes cannot be empty")
        max_prime = max(primes)
        assert isinstance(max_prime, int)
        if size is None:
            size = max_prime

        instance = cls.__new__(cls)
        instance._data = sum((int(2**p) for p in primes))
        instance._n = size
        instance._count = instance._data.bit_count()
        return instance

    def __init__(self, data: int) -> None:
        self._data: int = data
        self._n = self._data.bit_length()
        self._count = self._data.bit_count()

    def _extend(self, n: int) -> None:
        if n <= self._data.bit_length():
            return
        ones = (2 ** ((n - self._n) + 1)) - 1
        ones = ones << self._n
        self._data |= ones

        self._n = n
        # We only need to go up to and including the square root of n,
        # remove all non-primes above that square-root =< n.
        for p in range(2, isqrt(n) + 1):
            # if utils.get_bit(self._data, p):
            if (self._data & (1 << p)) >> p:
                # Because we are going through sieve in numeric order
                # we know that multiples of anything less than p have
                # already been removed, so p is prime.
                # Our job is to now remove multiples of p
                # higher up in the sieve.
                for m in range(p + p, n + 1, p):
                    # self._data = utils.set_bit(self._data, m, False)
                    self._data = self._data & ~(1 << m)

    @classmethod
    def from_size[S](cls, size: int) -> "IntSieve":
        if size < 2:
            raise ValueError("size must be greater than 2")

        instance = cls.__new__(cls)

        instance._data = instance._BASE_SIEVE
        instance._n = instance._BASE_SIEVE.bit_length()
        instance._extend(size)
        instance._count = instance._data.bit_count()
        return instance

    def nth_prime(self, n: int) -> int:
        if n < 1:
            raise ValueError("n must be greater than zero")

        if n > self.count:
            raise ValueError("n cannot exceed count")

        result = bit_utils.bit_index(self._data, n)
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
            pm = bit_utils.bit_index(self._data, n)
            assert pm is not None
            yield pm

    def __int__(self) -> int:
        return self._data

    # 'Inherit' docstrings
    from_size.__doc__ = Sievish.from_size.__doc__
    __int__.__doc__ = Sievish.__int__.__doc__
    primes.__doc__ = Sievish.primes.__doc__
    reset.__doc__ = Sievish.reset.__doc__
    nth_prime.__doc__ = Sievish.nth_prime.__doc__
    from_int.__doc__ = Sievish.from_int.__doc__
    from_list.__doc__ = Sievish.from_list.__doc__


# https://mypy.readthedocs.io/en/stable/common_issues.html#variables-vs-type-aliases
Sieve: type[object]
"""Sieve will be an alias for BaSieve if bitarray is available,
otherwise it will be assigned to some other sieve class."""

if _has_bitarry:
    Sieve = BaSieve
else:
    Sieve = SetSieve
