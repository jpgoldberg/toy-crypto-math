import os
import sys
import timeit

PROJECT_PATH = os.getcwd()
SOURCE_PATH = os.path.join(PROJECT_PATH, "src")
sys.path.append(SOURCE_PATH)

from toy_crypto.nt import Sieve  # noqa: E402

setup = """
from toy_crypto.nt import Sieve
"""

FIRST_SIZE = 10_000_000
FINAL_SIZE = 100_000_000
TRIALS = 10

PRIME = 71
LEN = 100_000


def f1() -> None:
    Sieve.clear()
    Sieve(FIRST_SIZE)
    Sieve(FINAL_SIZE)


def f2() -> None:
    Sieve.clear()
    Sieve(FIRST_SIZE)
    Sieve.clear()
    Sieve(FINAL_SIZE)


def f_mod() -> int:
    r = LEN % PRIME
    if r == 0:
        return LEN
    return LEN + (PRIME - r)


t1 = timeit.Timer(stmt=f1).timeit(number=10)
print(f"time with cache: {t1}")

t2 = timeit.Timer(stmt=f2).timeit(number=10)
print(f"time with cache cleared: {t2}")
