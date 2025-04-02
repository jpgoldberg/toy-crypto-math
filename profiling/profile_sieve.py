import timeit
from typing import Protocol, Self
from toy_crypto import sieve

repetitions = 5
sieve_size = 500_000


class SieveLike(Protocol):
    @classmethod
    def reset(cls) -> None: ...

    count: int  # implemented as @property in most instances

    def __call__(self: Self, size: int) -> Self: ...  # this is new/init


def sieve_count(s_class: SieveLike, size: int) -> int:
    s_class.reset()
    s = s_class(size)
    return s.count


s_classes = [
    f"sieve.{c.__name__}"
    for c in (sieve.Sieve, sieve.IntSieve, sieve.SetSieve)
]
statements = [f"sieve_count({c}, {sieve_size})" for c in s_classes]

for stmt in statements:
    print(f"Timing '{stmt}")
    t = timeit.timeit(stmt=stmt, number=repetitions, globals=globals())
    print(t)
