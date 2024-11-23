from typing import Any, NewType, TypeGuard

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


Byte = NewType("Byte", int)


def is_byte(val: Any) -> TypeGuard[Byte]:
    """True iff val is int s.t. 0 <= val < 256."""
    if not isinstance(val, int):
        return False
    return 0 <= val and val < 256
