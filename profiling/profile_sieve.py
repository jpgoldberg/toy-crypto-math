import timeit
from toy_crypto import nt

repetitions = 5
sieve_size = 500_000


def ba_sieve() -> int:
    nt.Sieve.clear()
    s = nt.Sieve(sieve_size)
    return s.count


def int_sieve() -> int:
    s = nt.IntSieve(sieve_size)
    return s.count


statements = [
    "ba_sieve()",
    "int_sieve()",
]

for stmt in statements:
    print(f"Timing '{stmt}")
    t = timeit.timeit(stmt=stmt, number=repetitions, globals=globals())
    print(t)
