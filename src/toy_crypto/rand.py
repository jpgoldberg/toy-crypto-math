"""Supplements Python secrets module"""

import secrets


def randrange(start: int, stop: int, step: int = 1) -> int:
    diff = stop - start
    if diff < 1:
        raise ValueError("stop must be greater than start")

    if step < 1:
        raise ValueError("step must be positive")

    if diff == 1:
        return start

    r = secrets.randbelow(diff // step)
    r *= step
    r += start

    return r
