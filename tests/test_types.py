import sys

import pytest
from toy_crypto import types


class TestChar:
    @staticmethod
    @pytest.mark.parametrize(
        "thing, expected, note",
        [
            ("", False, "string too short"),
            ("a", True, "string just right"),
            ("ab", False, "string too long"),
            (["a"], False, "Right size, wrong type (list)"),
            (b"a", False, "Right size, wrong type (bytes)"),
            (1, False, "not Sized (int)"),
            (0.5, False, "not Sized (float)"),
            (pow, False, "not sized (function)"),
        ],
    )
    def test_is_char(thing: object, expected: bool, note: str) -> None:
        assert types.is_char(thing) is expected, note


class TestProb:
    @staticmethod
    @pytest.mark.parametrize(
        "thing, expected, note",
        [
            (0.0, True, "zero (float)"),
            (1.0, True, "one (float)"),
            (0, False, "zero (int)"),
            (1, False, "one (int)"),
            (1.1, False, "too big (float)"),
            (-0.1, False, "too small (float)"),
            (2, False, "too big (int)"),
            (-33, False, "too small (int)"),
            ("", False, "string too short"),
            ("a", False, "wrong type (str)"),
            (["a"], False, "wrong type (list)"),
            (pow, False, "wrong type (function)"),
        ],
    )
    def test_is_prob(thing: object, expected: bool, note: str) -> None:
        assert types.is_prob(thing) is expected, note


class TestDocstrings:
    def test_predicate_description(self) -> None:
        expected = (
            "True if and only if val satisfies all of"
            "\n- is of type int\n- meets ValueRange(0, 255)"
            "\n- meets LengthRange(1, 1)"
        )
        base_type: type = int
        constraints = (
            types.ValueRange(0, 255),
            types.LengthRange(1, 1),
        )
        d = types._predicate_description(base_type, constraints)
        assert d == expected


if __name__ == "__main__":
    sys.exit(pytest.main(args=[__file__]))
