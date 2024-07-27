from toy_crypto.nt import lcm, modinv


class PublicKey:
    def __init__(self, modulus: int, public_exponent: int) -> None:
        self._N = modulus
        self._e = public_exponent

    @property
    def N(self) -> int:
        return self._N

    @property
    def e(self) -> int:
        return self._e

    def encrypt(self, message: int) -> int:
        """raw encryption with neither padding nor nonce"""
        if message < 0:
            raise ValueError("Positive messages only")
        if not message < self._N:
            raise ValueError("Message too big")

        return pow(base=message, exp=self._e, mod=self._N)

    def __eq__(self, other: object) -> bool:
        """True when each has the same modulus and public exponent.

        When comparing to a PrivateKey, this compares only the public parts.
        """
        if isinstance(other, PublicKey):
            return self.e == other.e and self.N == other.N

        return NotImplemented


class PrivateKey:
    DEFAULT_E = 65537

    def __init__(self, p: int, q: int, pub_exponent: int = DEFAULT_E) -> None:
        self._p = p
        self._q = q
        self._e = pub_exponent

        self._N = self._p * self._q
        self._pubkey = PublicKey(self._N, self._e)

        self._dP = modinv(self._e, p - 1)
        self._dQ = modinv(self._e, (self._q - 1))
        self._qInv = modinv(self._q, self._p)

        self._d = self._compute_d()

    @property
    def pub_key(self) -> PublicKey:
        return self._pubkey

    @property
    def e(self) -> int:
        return self._e

    def __eq__(self, other: object) -> bool:
        """True iff keys are mathematically equivalent

        Private keys with internal differences can behave identically
        with respect to input and output. This comparison will return
        True when they are equivalent in this respect.

        When compared to a PublicKey, this compares only the public part.
        """
        if isinstance(other, PrivateKey):
            return self.pub_key == other.pub_key

        if isinstance(other, PublicKey):
            return self.pub_key == other

        return NotImplemented

    def _compute_d(self) -> int:
        λ = lcm(self._p - 1, self._q - 1)
        try:
            return modinv(self.e, λ)
        except ValueError:
            raise ValueError("Inverse of e mod λ does not exist")

    def decrypt(self, ciphertext: int) -> int:
        """Decrypt ciphertext"""

        if ciphertext < 1 or ciphertext >= self.pub_key.N:
            raise ValueError("ciphertext is out of range")

        # m =  pow(base=ciphertext, exp=self._d, mod=self._N)
        # but we will use the CRT
        # version comes from  rfc8017 §5.1.2

        m_1 = pow(ciphertext, self._dP, self._p)
        m_2 = pow(ciphertext, self._dQ, self._q)

        # I need to review CRT to see what this is for
        h = ((m_1 - m_2) * self._qInv) % self._p

        m = m_2 + self._q * h
        return m
