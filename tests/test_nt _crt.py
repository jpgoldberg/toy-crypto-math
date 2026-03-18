import sys

import pytest
from toy_crypto.nt import crt

class TestSolve:
    def test_solve(self) -> None:
        f = crt.Ring((4, 9, 25))
        remainders = (3, 1, 14)
        expected = 739

        result = f.to_int(remainders)
        assert result == expected


if __name__ == "__main__":
    sys.exit(pytest.main(args=[__file__]))
