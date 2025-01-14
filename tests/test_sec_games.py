import secrets
import sys

import pytest
from toy_crypto.sec_games import IndEav, IndCpa, StateError, IndCca2


class TestInd:
    """
    For reliable tests, we will need a encryption scheme that the adversary
    can win against all the time.
    """

    def encryptor(self, key: int, m: bytes) -> bytes:
        encrypted: bytes = bytes([(b + key) % 256 for b in m])
        return encrypted

    def decryptor(self, key: int, m: bytes) -> bytes:
        encrypted: bytes = bytes([(b - key) % 256 for b in m])
        return encrypted

    def key_gen(self) -> int:
        return secrets.randbelow(256)

    def test_eav(self) -> None:
        challenger = IndEav(self.key_gen, self.encryptor)

        m0 = b"AA"
        m1 = b"AB"

        # chance of false pass is 2^trials
        trials = 20
        for _ in range(trials):
            challenger.initialize()
            ctext = challenger.encrypt_one(m0, m1)
            guess: bool = ctext[0] != ctext[1]

            assert challenger.finalize(guess)

    def test_eav_once(self) -> None:
        challenger = IndEav(self.key_gen, self.encryptor)
        m0 = b"AA"
        m1 = b"AB"

        challenger.initialize()

        _ = challenger.encrypt_one(m0, m1)

        with pytest.raises(StateError):
            _ = challenger.encrypt_one(m0, m1)

    def test_cpa_deterministic(self) -> None:
        """Wins against deterministic encryption"""
        challenger = IndCpa(self.key_gen, self.encryptor)

        m0 = b"Attack at dawn!"
        m1 = b"Attack at dusk!"

        # chance of false pass is 2^trials
        trials = 20
        for _ in range(trials):
            challenger.initialize()
            ctext1 = challenger.encrypt_one(m0, m1)
            ctext2 = challenger.encrypt_one(m1, m1)
            guess = ctext1 == ctext2

            assert challenger.finalize(guess)

        """Wins against deterministic encryption"""
        challenger = IndCpa(self.key_gen, self.encryptor)

        m0 = b"Attack at dawn!"
        m1 = b"Attack at dusk!"

        # chance of false pass is 2^trials
        trials = 20
        for _ in range(trials):
            challenger.initialize()
            ctext1 = challenger.encrypt_one(m0, m1)
            ctext2 = challenger.encrypt_one(m1, m1)
            guess = ctext1 == ctext2

            assert challenger.finalize(guess)

    def test_cca2(self) -> None:
        """Wins against deterministic encryption.

        I should construct a test that distinguishes CPA and CCA,
        but this is not that test
        """
        challenger = IndCca2(
            key_gen=self.key_gen,
            encryptor=self.encryptor,
            decrytpor=self.decryptor,
        )

        m0 = b"Attack at dawn!"
        m1 = b"Defend at dusk!"
        cct1 = b"AAAAAAA"

        # chance of false pass is 2^trials
        trials = 20
        for _ in range(trials):
            challenger.initialize()
            c0 = challenger.encrypt(m0)
            ctext = challenger.encrypt_one(m0, m1)

            if c0 == ctext:
                first_guess = 0
            else:
                first_guess = 1

            # let's use a chosen ciphertext to break this
            # even though it could be broken otherwise.
            ptext = challenger.decrypt(cct1)
            key_guess = cct1[0] - ptext[0] % 256
            if (m1[0] + key_guess) % 256 == ctext[0]:
                second_guess = 1
            else:
                second_guess = 0

            assert first_guess == second_guess

            assert challenger.finalize(first_guess)

    def test_cca1(self) -> None:
        """Wins against deterministic encryption.

        I should construct a test that distinguishes CPA and CCA,
        but this is not that test
        """
        challenger = IndCca2(
            key_gen=self.key_gen,
            encryptor=self.encryptor,
            decrytpor=self.decryptor,
        )

        m0 = b"Attack at dawn!"
        m1 = b"Defend at dusk!"
        cct1 = b"AAAAAAA"

        # chance of false pass is 2^trials
        trials = 20
        for _ in range(trials):
            challenger.initialize()

            # let's use a chosen ciphertext to break this
            # even though it could be broken otherwise.
            ptext = challenger.decrypt(cct1)
            key_guess = cct1[0] - ptext[0] % 256

            ctext = challenger.encrypt_one(m0, m1)

            if (m1[0] + key_guess) % 256 == ctext[0]:
                first_guess = 1
            else:
                first_guess = 0

            c0 = challenger.encrypt(m0)

            if c0 == ctext:
                second_guess = 0
            else:
                second_guess = 1

            assert first_guess == second_guess

            assert challenger.finalize(first_guess)

    def test_cca2_ctext_clear(self) -> None:
        """Previous round banned ctext allowed.

        This tests a bug in which the list of banned ciphertexts that
        can be given to decrypt() wasn't clear with re-initialization.
        """
        challenger = IndCca2(
            key_gen=self.key_gen,
            encryptor=self.encryptor,
            decrytpor=self.decryptor,
        )

        m0 = b"Attack at dawn!"
        m1 = b"Defend at dusk!"
        x = b"B"
        cct1 = b"AAAAAAA"

        challenger.initialize()
        _ = challenger.decrypt(cct1)
        ctext = challenger.encrypt_one(m0, m1)

        with pytest.raises(Exception):
            _ = challenger.decrypt(ctext)

        # check that both encrypt and decrypt can still be called
        c_x = challenger.encrypt(x)
        p_x = challenger.decrypt(c_x)
        assert p_x == x
        _ = challenger.finalize(0)

        # Now the thing we really aim to test here.
        challenger.initialize()
        _ = challenger.decrypt(c_x)

        new_ctext = challenger.encrypt_one(b"X", b"Y")

        # This call should be allowed
        _ = challenger.decrypt(ctext)

        with pytest.raises(Exception):
            _ = challenger.decrypt(new_ctext)


if __name__ == "__main__":
    sys.exit(pytest.main(args=[__file__]))
