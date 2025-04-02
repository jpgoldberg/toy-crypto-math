from typing import Any, Iterator, Optional, Protocol, runtime_checkable, Self

from . import utils
from math import isqrt

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
class SieveLike(Protocol):
    @classmethod
    def reset(cls) -> None: ...

    @property
    def count(self) -> int: ...

    @property
    def n(self) -> int: ...

    def primes(self, start: int = 1) -> Iterator[int]: ...

    def to01(self) -> str: ...

    # def extend(self, n: int) -> None: ...

    def __int__(self) -> int: ...

    def __call__(self: Self, size: int) -> Self: ...


class Sieve:
    """Sieve of Eratosthenes.

    The good parts of this implementation are lifted from the example provided
    with the `bitarray package <https://pypi.org/project/bitarray/>`_ source.

    This depends on `bitarray package <https://pypi.org/project/bitarray/>`_.
    """

    _base_sieve = bitarray("0011")

    def extend(self, n: int) -> None:
        """Extends the the current sieve"""
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
        """No-op until I rethink the whole cashing thing."""
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
        """The sieve as a string of 0s and 1s.

        The output is to be read left to right. That is, it should begin with
        ``001101010001`` corresponding to primes [2, 3, 5, 7, 11]
        """

        if self._bitstring is None:
            self._bitstring = self._sieve[: self._n].to01()
        return self._bitstring

    def nth_prime(self, n: int) -> int:
        """Returns n-th prime.

        :raises ValueError: if n exceeds count.
        """

        if n > self._count:
            raise ValueError("n cannot exceed count")

        return count_n(self._sieve, n)

    def primes(self, start: int = 1) -> Iterator[int]:
        """Iterator of primes starting at start-th prime.

        The 1st prime is 2. There is no zeroth prime.

        :raises ValueError: if start < 1
        """
        if start < 1:
            raise ValueError("Start must be >= 1")
        for n in range(start, self._count + 1):
            yield count_n(self._sieve, n) - 1

    def __int__(self) -> int:
        reversed = self._sieve.copy()[: self._n]
        reversed.reverse()
        return ba2int(reversed)


class SetSieve:
    """Sieve of Eratosthenes using a native python set

    This consumes an enormous amount of early in initialization,
    and a SetSieve object will contain a list of prime integers,
    so even after initialization is requires more memory than the
    the integer or bitarray sieves.
    """

    _base_sieve: list[int] = [2, 3]

    def extend(self, n: int) -> None:
        """Extends the the current sieve"""
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
        """Reset the cached sieve.

        This is a no-op if the class doesn't
        actually cache the largest sieve created.
        """

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

    @property
    def count(self) -> int:
        return len(self._sieve)

    def primes(self, start: int = 1) -> Iterator[int]:
        """Iterator of primes starting at start-th prime.

        The 1st prime is 2. There is no zeroth prime.

        :raises ValueError: if start < 1
        """
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
        """The sieve as a string of 0s and 1s.

        The output is to be read left to right. That is, it should begin with
        ``001101010001`` corresponding to primes [2, 3, 5, 7, 11]
        """

        return format(self.__int__(), "b")[::-1]


class IntSieve:
    """A pure Python (using a large int) Sieve of Eratosthenes."""

    @classmethod
    def reset(cls) -> None:
        """Reset the cached sieve.

        This is a no-op if the class doesn't
        actually cache the largest sieve created.
        """

        pass

    def __init__(self, n: int) -> None:
        """Creates sieve of primes <= n"""

        self._length = n
        if n < 2:
            raise ValueError

        self._sieve: int = (2 ** (n + 1)) - 1
        self._sieve -= 3  # unset 0th and 1st bit.

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

        self._count = self._sieve.bit_count()

    def to01(self) -> str:
        """The sieve as a string of 0s and 1s.

        The output is to be read left to right. That is, it should begin with
        ``001101010001`` corresponding to primes [2, 3, 5, 7, 11]
        """

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
        return self._length

    def primes(self, start: int = 1) -> Iterator[int]:
        """Iterator of primes starting at start-th prime.

        The 1st prime is 2. There is no zeroth prime.

        :raises ValueError: if start < 1
        """
        if start < 1:
            raise ValueError("Start must be >= 1")
        for n in range(start, self.count + 1):
            pm = utils.bit_index(self._sieve, n)
            assert pm is not None
            yield pm

    def __int__(self) -> int:
        return self._sieve
