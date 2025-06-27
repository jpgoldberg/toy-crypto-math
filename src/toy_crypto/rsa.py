from dataclasses import dataclass
import hashlib
from hmac import compare_digest
import math
import secrets
from typing import Callable
from toy_crypto import utils
from toy_crypto.nt import lcm, modinv

_DEFAULT_E = 65537


def default_e() -> int:
    """Returns the default public exponent, 65537"""
    return _DEFAULT_E


class DecryptionError(Exception):
    """
    For secure implementations it is important to not
    report why a decryption failed.

    But for this implementation we will do the opposite.
    We will be very revealing about decryption failures.
    """


type HashFunc = Callable[[bytes], hashlib._Hash]
"""Type for hashlib style hash function."""

type MgfFunc = Callable[[bytes, int, str], bytes]
"""Type for RFC8017 Mask Generation Function."""


class Oaep:
    """
    Tools and data for OAEP.

    Although this attempts to follow RFC8017 in many
    respects, this is not designed to be interoperable
    with compliant keys and ciphertext.
    """

    @dataclass(frozen=True, kw_only=True)
    class HashInfo:
        """Information about hash function

        Note that names and identifiers here do not
        conform to RFCs. These are not mean to be interoperable
        with anything out in the world.
        """

        hashlib_name: str
        function: HashFunc
        digest_size: int  # in bytes
        input_limit: int  # maximum input, in bytes

    @dataclass(frozen=True, kw_only=True)
    class MgfInfo:
        """Information about Mask Generation function"""

        algorithm: str  # eg "id-mfg1"
        hashAlgorithm: str  # Key in KNOWN_HASHES
        function: MgfFunc

    @staticmethod
    def mgf1(
        seed: bytes,  # There do not appear to be any constraints on this
        length: int,  # Output length
        hash_id: str,  # key for KNOWN_HASHES
    ) -> bytes:
        """Mask generation function.

        Generates a unique mask of length :data:`length`.

        :param seed: This should come from a CSPRNG
        :param length: Length in bytes of the mask to generate.
        :param hash_id: The name hash function in :data:`KNOWN_HASHES`.

        :raises ValueError: if :data:`length` :math:`> 2^{32}` bytes.
        :raises ValueError: if :data:`hash_id` is unknown.

        From https://datatracker.ietf.org/doc/html/rfc8017#appendix-B.2.1

        This would have been a lot simpler if :rfc:`HKDF <5896>`
        had been around before :rfc:`3447`.
        """

        """
        I am using Pythonic variable naming instead of what is in the RFC

        RFC Name | My name | Description                        | Type
        -----------------------------------------------------------------
        mfgSeed | seed      | seed from which mask is generated | bytes
        maskLen | length    | Intended length of mask           | int
        mask    | mask      | Output                            | bytes
        T       | t         | Internal array for building mask  | bytearray
        C       | counter   | Counter, four octets              | bytes
                | hash_id   | ID of hash function               | str
        Hash    | hasher    | CS hash function                  | HashFunc
        """

        if length > 2**32:
            raise ValueError("mask too long")

        try:
            hash = Oaep.KNOWN_HASHES[hash_id]
        except KeyError:
            raise ValueError(f'Unsupported hash function: "{hash_id}')

        digest_size = hash.digest_size
        hasher = hash.function

        t = bytearray()

        # "For counter from 0 to \ceil (maskLen / hLen) - 1, ..."
        # range is not inclusive at high end. So we need to add one
        for c in range(math.ceil(length / digest_size) - 1 + 1):
            counter = Oaep.i2osp(c, 4)
            assert len(counter) == 4
            digest = hasher(seed + counter).digest()
            t.extend(digest)

        assert len(t) >= length
        mask = bytes(t[:length])
        return mask

    KNOWN_HASHES: dict[str, HashInfo] = {
        "sha256": HashInfo(
            hashlib_name="sha256",
            function=hashlib.sha256,
            digest_size=32,
            input_limit=2**61 - 1,
        ),
        # We need sha1 because that is what test vectors exist for
        "sha1": HashInfo(
            hashlib_name="sha1",
            function=hashlib.sha1,
            digest_size=20,
            input_limit=2**64 - 1,
        ),
    }
    """Hashes known for OAEP. keys will be hashlib names."""

    KNOWN_MFGS: dict[str, MgfInfo] = {
        "mgf1SHA256": MgfInfo(
            algorithm="id_mgf1", hashAlgorithm="sha256", function=mgf1
        ),
        "mgf1SHA1": MgfInfo(
            algorithm="id_mgf1", hashAlgorithm="sha1", function=mgf1
        ),
    }
    """Known Mask Generation Functions."""

    @staticmethod
    def i2osp(n: int, length: int) -> bytes:
        """Integer to an octet string of length length.

        :param n: A non-negative integer
        :param length: Length of returned bytes object

        :raises ValueError: if :data:`n` is negative.
        :raises ValueError: if :data:`n` cannot fit in :data:`length` bytes


        All operations big-endian.

        https://datatracker.ietf.org/doc/html/rfc8017#section-4.1
        """

        if n < 0:
            raise ValueError("Number cannot be negative")

        if (n.bit_length() + 7) // 8 > length:
            raise ValueError("input is too large for the given length")

        return n.to_bytes(length, byteorder="big", signed=False)

    @staticmethod
    def os2ip(x: bytes) -> int:
        """octet-stream to unsigned big-endian int.

        :param x:
            The octet-stream (:py:class:`bytes`) you want
            to make an :py:class:`int` from.

        Returned is a non-negative integer.

        All operations are big-endian.

        https://datatracker.ietf.org/doc/html/rfc8017#section-4.1
        """
        return int.from_bytes(x, byteorder="big", signed=False)


class PublicKey:
    def __init__(self, modulus: int, public_exponent: int) -> None:
        """Public key from public values."""
        self._N = modulus
        self._e = public_exponent

    @property
    def N(self) -> int:
        """Public modulus N."""
        return self._N

    @property
    def e(self) -> int:
        """Public exponent e"""
        return self._e

    def encrypt(self, message: int) -> int:
        """Primitive encryption with neither padding nor nonce.

        :raises ValueError: if message < 0
        :raises ValueError: if message isn't less than the public modulus
        """

        if message < 0:
            raise ValueError("Positive messages only")

        """
        There is a reason for the explicit conversion to int in the
        comparison below. If message was created as a member of a SageMath
        finite group mod N, self._N would be converted to that before
        comparison and self._N ≡ 0 (mod self._N).
        """
        if not int(message) < self._N:
            raise ValueError("Message too big")

        return pow(base=message, exp=self._e, mod=self._N)

    def oaep_encrypt(
        self,
        message: bytes,
        label: bytes = b"",
        hash_id: str = "sha256",
        mgf_id: str = "mgf1SHA256",
        _seed: bytes | None = None,  # For testing only
    ) -> bytes:
        """
        RSA OAEP encryption.

        :param message: The message to encrypt.
        :param label: Rarely used. Just leave as default.
        :param hash_id: Name of the hash function.
        :param mgf_id: Name of the MGF function (with hash).
        :param _seed: Used for testing only. OAEP is not supposed to be deterministic.

        :raises ValueError: if hash or MGF is not recognized.
        :raises ValueError:
            if lengths of inputs exceed what modulus and hash sizes
            can accommodate.

        https://datatracker.ietf.org/doc/html/rfc8017#section-7.1.1
        """

        try:
            h = Oaep.KNOWN_HASHES[hash_id]
        except KeyError:
            raise ValueError(f'Unsupported hash: "{hash_id}')

        try:
            mgf = Oaep.KNOWN_MFGS[mgf_id]
        except KeyError:
            raise ValueError(
                f'Unsupported mask generation function: "{mgf_id}'
            )

        if len(label) > h.input_limit:
            raise ValueError("label too long")

        k = self.N.bit_length() // 8  # length of N in bytes

        if len(message) > k - 2 * h.digest_size - 2:
            raise ValueError("message too long")

        lhash = h.function(label).digest()

        ps_length = k - len(message) - 2 * h.digest_size - 2
        padding_string = bytes(ps_length)

        data_block = lhash + padding_string + bytes([0x01]) + message

        # So that we can test with a set seed
        seed: bytes
        if _seed is None:
            seed = secrets.token_bytes(h.digest_size)
        else:
            seed = _seed

        mask = mgf.function(seed, k - h.digest_size - 1, mgf.hashAlgorithm)
        masked_db = utils.xor(data_block, mask)
        seed_mask = mgf.function(masked_db, h.digest_size, mgf.hashAlgorithm)
        masked_seed = utils.xor(seed, seed_mask)

        encoded_m = bytes([0x00]) + masked_seed + masked_db
        m = Oaep.os2ip(encoded_m)
        ctext = self.encrypt(m)

        return Oaep.i2osp(ctext, k)

    def __eq__(self, other: object) -> bool:
        """True when each has the same modulus and public exponent.

        When comparing to a PrivateKey, this compares only the public parts.
        """
        if isinstance(other, PublicKey):
            return self.e == other.e and self.N == other.N

        return NotImplemented


class PrivateKey:
    def __init__(self, p: int, q: int, pub_exponent: int = _DEFAULT_E) -> None:
        """RSA private key from primes p and q.

        This does not perform any sanity checks on p and q.
        It is your responsibility to ensure that p and q are prime

        :raises ValueError: if e is not coprime with lcm(p - 1, q - 1).
        """

        self._p = p
        self._q = q
        self._e = pub_exponent

        self._N = self._p * self._q
        self._pubkey = PublicKey(self._N, self._e)

        self._dP = modinv(self._e, p - 1)
        self._dQ = modinv(self._e, (self._q - 1))
        self._qInv = modinv(self._q, self._p)

        try:
            self._d = self._compute_d()
        except ValueError:
            raise ValueError("p, q, and e are incompatible with each other ")

    @property
    def pub_key(self) -> PublicKey:
        """The public key corresponding to self.

        The public key does not contain any secrets.
        """

        return self._pubkey

    @property
    def e(self) -> int:
        """Public exponent."""
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
        """Primitive decryption."""

        ciphertext = int(ciphertext)  # See comment in PublicKey.encrypt()

        if ciphertext < 1 or ciphertext >= self.pub_key.N:
            raise DecryptionError("ciphertext is out of range")

        # m =  pow(base=ciphertext, exp=self._d, mod=self._N)
        # but we will use the CRT
        # version comes from  rfc8017 §5.1.2

        m_1 = pow(ciphertext, self._dP, self._p)
        m_2 = pow(ciphertext, self._dQ, self._q)

        # CRT for the win!
        h = ((m_1 - m_2) * self._qInv) % self._p

        m = m_2 + self._q * h
        return m

    def oaep_decrypt(
        self,
        ciphertext: bytes,
        label: bytes = b"",
        hash_id: str = "sha256",
        mgf_id: str = "mgf1SHA256",
    ) -> bytes:
        """
        RSA OAEP decryption.

        :param ciphertext: The message to encrypt.
        :param label: Rarely used.
        :param hash_id: Name of the hash function.
        :param mgf_id: Name of the MGF function (with hash).

        :raises ValueError: if hash or MGF is not recognized.
        :raises DecryptionError:
            on various decryption errors.
            Note that these messages provide specific reasons for decryption
            failure. That behavior enables CCA attacks on OAEP.

        https://datatracker.ietf.org/doc/html/rfc8017#section-7.1.2
        """

        try:
            h = Oaep.KNOWN_HASHES[hash_id]
        except KeyError:
            raise ValueError(f'Unsupported hash: "{hash_id}')

        try:
            mgf = Oaep.KNOWN_MFGS[mgf_id]
        except KeyError:
            raise ValueError(
                f'Unsupported mask generation function: "{mgf_id}'
            )
        k = self.pub_key.N.bit_length() // 8  # length of N in bytes

        # Don't be explicit about decryption is serious code.
        # This is toy code.
        if len(label) > h.input_limit:
            raise DecryptionError("Label too long")

        if len(ciphertext) != k:
            raise DecryptionError("Ciphertext is wrong size")

        if k < 2 * h.digest_size + 2:
            raise DecryptionError("Modulus is way too short")

        c = Oaep.os2ip(ciphertext)
        m = self.decrypt(c)
        em = Oaep.i2osp(m, k)

        lhash = h.function(label).digest()

        # We split em into three parts (Step 3b)
        y: int = em[0]
        masked_seed: bytes = em[1 : h.digest_size + 1]
        masked_datablock: bytes = em[h.digest_size + 1 :]

        # Steps 3c-f
        seed_mask = mgf.function(
            masked_datablock, h.digest_size, mgf.hashAlgorithm
        )
        seed = utils.xor(masked_seed, seed_mask)
        db_mask = mgf.function(seed, k - h.digest_size - 1, mgf.hashAlgorithm)
        data_block = utils.xor(masked_datablock, db_mask)

        # Split the data block. Step 3g
        lhash_prime: bytes = data_block[: h.digest_size]
        remainder: bytes = data_block[h.digest_size :].lstrip(bytes([0]))
        one: int = remainder[0]
        message: bytes = remainder[1:]

        # Checks on all of that are standardly deferred to avoid
        # timing on failure reason.
        # We aren't worried about that in this toy code, but follow
        # the sequence anyway.

        # Revealing why decryption fails opens things up
        # for chosen ciphertext attacks. Don't do what I do here.

        if one != 1:
            raise DecryptionError("Expected 0x01")
        if not compare_digest(lhash, lhash_prime):
            raise DecryptionError("Label mismatch")
        if y != 0:
            raise Exception("Expected 0x00 prefix")

        return message
