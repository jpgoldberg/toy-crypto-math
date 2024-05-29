from typing import NewType, TypeGuard, Any
from toy_crypto.nt import isprime


Prob = NewType("Prob", float)


def is_prob(val: Any) -> TypeGuard[Prob]:
    """true if val is a float, s.t. 0.0 <= va <= 1.0"""
    if not isinstance(val, float):
        return False
    return val >= 0.0 and val <= 1.0


PositiveInt = NewType("PositiveInt", int)


def is_positive_int(val: Any) -> TypeGuard[PositiveInt]:
    """true if val is a float, s.t. 0.0 <= va <= 1.0"""
    if not isinstance(val, int):
        return False
    return val >= 1


Modulus = NewType("Modulus", int)


def is_modulus(n: Any) -> TypeGuard[Modulus]:
    if not isinstance(n, int):
        return False
    if n < 2:
        return False
    if not isprime(n):
        return False
    return True
