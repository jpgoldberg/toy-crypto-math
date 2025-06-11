import os
import sys
import time

PROJECT_PATH = os.getcwd()
SOURCE_PATH = os.path.join(PROJECT_PATH, "src")
sys.path.append(SOURCE_PATH)

from toy_crypto.sieve import BaSieve  # noqa: E402

setup = """
from toy_crypto.sieve import Sieve
"""

FIRST_SIZE = 10_000_000
FINAL_SIZE = 100_000_000
TRIALS = 10

PRIME = 71
LEN = 100_000


def f1() -> None:
    BaSieve._reset()
    s1 = BaSieve.from_size(FIRST_SIZE)
    assert s1.count == 664579
    s2 = BaSieve.from_size(FINAL_SIZE)
    assert s2.count == 5761455


def f2() -> None:
    BaSieve._reset()
    s1 = BaSieve.from_size(FIRST_SIZE)
    assert s1.count == 664579
    BaSieve._reset()
    s2 = BaSieve.from_size(FINAL_SIZE)
    assert s2.count == 5761455


def f3() -> None:
    BaSieve._reset()
    s1 = BaSieve.from_size(FIRST_SIZE)
    s2 = BaSieve.from_size(FIRST_SIZE)
    assert s1.count == s2.count


def f4() -> None:
    BaSieve._reset()
    s1 = BaSieve.from_size(FIRST_SIZE)
    BaSieve._reset()
    s2 = BaSieve.from_size(FIRST_SIZE)
    assert s1.count == s2.count


def main() -> None:
    trials = 5

    t_f2_start = time.time()
    for _ in range(trials):
        f2()
    delta_f2 = time.time() - t_f2_start

    t_f1_start = time.time()
    for _ in range(trials):
        f1()
    delta_f1 = time.time() - t_f1_start

    print(
        f"For {FIRST_SIZE}, {FINAL_SIZE}\n"
        f"\t{delta_f1}/{delta_f2} = {delta_f1 / delta_f2:.2f}"
    )

    t_f3_start = time.time()
    for _ in range(trials):
        f3()
    delta_f3 = time.time() - t_f3_start

    t_f4_start = time.time()
    for _ in range(trials):
        f4()
    delta_f4 = time.time() - t_f4_start

    print(
        f"For {FIRST_SIZE}, {FIRST_SIZE}\n"
        f"\t{delta_f3}/{delta_f4} = {delta_f3 / delta_f4:.2f}"
    )


if __name__ == "__main__":
    main()
