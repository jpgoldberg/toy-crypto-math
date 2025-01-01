import secrets
import sys

import pytest
from toy_crypto.sec_games import IndEav


class TestIndCPA:
    """
    For reliable tests, we will need a encryption scheme that the adversary
    can win against all the time.
    """

    def encryptor(self, key: int, m: bytes) -> bytes:
        encrypted: bytes = bytes([(b + key) % 256 for b in m])
        return encrypted

    def key_gen(self) -> int:
        return secrets.randbelow(256)

    def test_cpa(self) -> None:
        challenger = IndEav(self.key_gen, self.encryptor)

        m0 = b"AA"
        m1 = b"AB"

        challenger.initialize()
        ctext = challenger.encrypt_one(m0, m1)

        guess: bool = ctext[0] != ctext[1]

        assert challenger.finalize(guess)


if __name__ == "__main__":
    sys.exit(pytest.main(args=[__file__]))
