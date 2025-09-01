from dataclasses import dataclass
import hashlib
from hmac import compare_digest
import math
import secrets
from typing import Callable
from toy_crypto import utils
from toy_crypto.nt import lcm, modinv, probably_prime, gcd

_DEFAULT_E = 65537


def default_e() -> int:
    """Returns the default public exponent, 65537"""
    return _DEFAULT_E


class DecryptionError(Exception):
    """
    For secure implementations it is important to not
    report why a decryption failed.

    See :meth:`Oaep.allow_unsafe_messages` to enable
    reasons why decryption fails.
    """


type HashFunc = Callable[[bytes], hashlib._Hash]
"""Type for hashlib style hash function."""

type MgfFunc = Callable[[bytes, int, str], bytes]
"""Type for RFC8017 Mask Generation Function."""


class Oaep:
    """
    Tools and data for OAEP.

    Although this attempts to follow :rfc:`8017` in many
    respects, this is not designed to be interoperable
    with compliant keys and ciphertext.
    """

    _unsafe_messages: str = "forbid"
    """Anything other than "allow" will keep DecryptionError messages safe."""

    @classmethod
    def allow_unsafe_messages(cls, allow: bool = True) -> None:
        """Allow (or disallow) verbose DecryptionError messages."""

        cls._unsafe_messages = "allow" if allow else "forbid"

    @classmethod
    def are_unsafe_messages_allowed(cls) -> bool:
        """Does what it says on the tin."""

        if cls._unsafe_messages == "allow":
            return True
        return False

    @classmethod
    def _unsafe_msg(cls, message: str) -> str:
        if cls._unsafe_messages == "allow":
            return message
        return "Not telling, nohow!"

    @dataclass(frozen=True, kw_only=True)
    class HashInfo:
        """Information about hash function

        :param hashlib_name: Name as known by hashlib
        :param function: The callable function
        :param digest_size: in bytes
        :param input_limit: in bytes

        Note that names and identifiers here do not
        conform to RFCs. These are not mean to be interoperable
        with anything out in the world.
        """

        #: Name as known by hashlib
        hashlib_name: str
        function: HashFunc  #: The callable function itself
        digest_size: int  #: in bytes
        input_limit: int  #: maximum input, in bytes

    @dataclass(frozen=True, kw_only=True)
    class MgfInfo:
        """Information about Mask Generation function.

        :param algorithm: Name of the algorithm.
        :param hashAlgorithm: Key in :data:`KNOWN_HASHES`.
        :param function: A Callable mask generation function
        """

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

        Generates a unique mask of length :data:`length` as described in
        :rfc:`appendix B.2.1 <8017#appendix-B.2.1>` of :rfc:`8017`.

        :param seed: This should come from a CSPRNG
        :param length: Length in bytes of the mask to generate.
        :param hash_id: The name hash function in :data:`KNOWN_HASHES`.

        :raises ValueError: if :data:`length` :math:`> 2^{32}` bytes.
        :raises ValueError: if :data:`hash_id` is unknown.
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

    KNOWN_MGFS: dict[str, MgfInfo] = {
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

        Implements function from :rfc:`RFC 8017 §4.1 <8017#section-4.1>`.

        :param n: A non-negative integer
        :param length: Length of returned bytes object

        :raises ValueError: if :data:`n` is negative.
        :raises ValueError: if :data:`n` cannot fit in :data:`length` bytes

        .. warning::

            When called from a decryption operation,
            exceptions should be caught and handled discretely.


        All operations big-endian.
        """

        if n < 0:
            raise ValueError("Number cannot be negative")

        if (n.bit_length() + 7) // 8 > length:
            raise ValueError("input is too large for the given length")

        return n.to_bytes(length, byteorder="big", signed=False)

    @staticmethod
    def os2ip(x: bytes) -> int:
        """octet-stream to unsigned big-endian int.

         Implements function from :rfc:`RFC 8017 §4.2 <8017#section-4.2>`.

        :param x:
            The octet-stream (:py:class:`bytes`) you want
            to make an :py:class:`int` from.

        Returned is a non-negative integer.

        All operations are big-endian.
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
        :param _seed:
            Used for testing only. OAEP is not supposed to be deterministic.

        :raises ValueError: if hash or MGF is not recognized.
        :raises ValueError:
            if lengths of inputs exceed what modulus and hash sizes
            can accommodate.

        :rfc:`8017#section-7.1.1`
        """

        try:
            h = Oaep.KNOWN_HASHES[hash_id]
        except KeyError:
            raise ValueError(f'Unsupported hash: "{hash_id}')

        try:
            mgf = Oaep.KNOWN_MGFS[mgf_id]
        except KeyError:
            raise ValueError(
                f'Unsupported mask generation function: "{mgf_id}'
            )

        if len(label) > h.input_limit:
            raise ValueError("label too long")

        k = (self.N.bit_length() + 7) // 8  # length of N in bytes

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
        It is your responsibility to ensure that they are suitable primes.
        Consider using :func:`fips186_prime_gen` to generate primes.

        :raises ValueError:
            if :math:`\\gcd(e, \\mathop{\\mathrm{lcm}}(p - 1, q - 1)) \\neq 1`.
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
        """Primitive decryption.

        :param ciphertext: Ciphertext as :py:class:`int`
        :raises ValueError: if :data:`ciphertext` is out of range for this key.

        """

        ciphertext = int(ciphertext)  # See comment in PublicKey.encrypt()

        if ciphertext < 1 or ciphertext >= self.pub_key.N:
            raise ValueError("ciphertext is out of range")

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
            If unsafe error reporting is enabled, details of
            decryption errors will be provided.

        """

        try:
            h = Oaep.KNOWN_HASHES[hash_id]
        except KeyError:
            raise ValueError(f'Unsupported hash: "{hash_id}')

        try:
            mgf = Oaep.KNOWN_MGFS[mgf_id]
        except KeyError:
            raise ValueError(
                f'Unsupported mask generation function: "{mgf_id}'
            )
        k = (
            self.pub_key.N.bit_length() + 7
        ) // 8  # ceil(length of N in bytes)

        # checks in Step 1 involve no secrets
        # Step 1.a
        if len(label) > h.input_limit:
            raise DecryptionError(Oaep._unsafe_msg("Label too long"))

        # Step 1.b
        if len(ciphertext) != k:
            raise DecryptionError(Oaep._unsafe_msg("Ciphertext is wrong size"))

        # Step 1.c
        if k < 2 * h.digest_size + 2:
            raise DecryptionError(Oaep._unsafe_msg("Modulus is way too short"))

        # Step 2.a
        c = Oaep.os2ip(ciphertext)

        # Step 2.b
        try:
            m = self.decrypt(c)
        except Exception as e:
            raise DecryptionError(
                Oaep._unsafe_msg(f"Primitive decryption error: {e}")
            )

        # Step 2.c
        # if k is computed correctly, conversion of bytes
        # should never fail.
        em = Oaep.i2osp(m, k)

        # Step 3 is where we perform validations that make use of secrets

        # Step 3.a is done before other tests to thwart certain timing attacks
        lhash = h.function(label).digest()

        # Step 3.b. Parse encoded message
        y: int = em[0]
        masked_seed: bytes = em[1 : h.digest_size + 1]
        masked_datablock: bytes = em[h.digest_size + 1 :]

        # Step 3.c and 3.d
        seed_mask = mgf.function(
            masked_datablock, h.digest_size, mgf.hashAlgorithm
        )
        seed = utils.xor(masked_seed, seed_mask)

        # Steps 3.e and 3.f
        db_mask = mgf.function(seed, k - h.digest_size - 1, mgf.hashAlgorithm)
        data_block = utils.xor(masked_datablock, db_mask)

        # Parsing portion of Step 3.g
        lhash_prime: bytes = data_block[: h.digest_size]
        remainder: bytes = data_block[h.digest_size :].lstrip(bytes([0]))
        if len(remainder) == 0:
            raise DecryptionError(Oaep._unsafe_msg("Negative message space"))
        one: int = remainder[0]
        message: bytes = remainder[1:]

        # Validation portion of Step 3.g
        if one != 1:
            raise DecryptionError(Oaep._unsafe_msg("Expected 0x01"))
        if not compare_digest(lhash, lhash_prime):
            raise DecryptionError(Oaep._unsafe_msg("Label mismatch"))
        if y != 0:
            raise DecryptionError(
                Oaep._unsafe_msg("Expected 0x00 leading byte")
            )

        return message


def key_gen(
    strength: int = 112,
    key_size: int = 2048,
    e: int = 65537,
) -> tuple[PublicKey, PrivateKey]:
    """Generates private key.

    :param strength: Intended security parameter (in bits).
    :param key_size: size in bits of desired modulus.
    :param e: public exponent.


    :raises ValueError:
        if bit_size is even smaller that the small values allowed by this toy.
    :raises ValueError:
        if bit_size doesn't correspond to an even number of bytes.
        (This is not a requirement of standards, but is of this implementation.)
    :raises ValueError: if e is out of range or is not odd.
    :raises ValueError: if key_size doesn't provide target strength.
    :raises Exception: if key that would be generated doesn't seem to work.
    :raises Exception: if prime generation fails.

    .. warning::

        This allows for the generation of unconscionably
        small keys. But that is ok, because this is a toy
        implementation in lots of other respects, too.

    Partially follows NIST SP 80056B, §6.3.1.
    """

    # Not going to mess with FIPS 186-5 C.1
    # So just set k = 5 to cover all reasonable cases.
    k = 5

    # Computation of d and CRT values is done by constructor.
    # So not all the checks will be performed in the same order
    # as in standards

    if strength > estimate_strength(key_size):
        raise ValueError(
            f"Requested key size ({key_size}) doesn't meet"
            "requested security level ({strength})"
        )

    if key_size < 512:
        raise ValueError(
            "any bit size under 2048 is unsafe. "
            "Anything under 512 can't be handled here"
        )

    # I think we only need it to be even, but lets make our primes
    # fit into a whole number of bytes.
    if key_size % 64 != 0:
        raise ValueError("bit_size must be a multiple of 64")

    if e % 2 != 1:
        raise ValueError("it is odd that e isn't odd")

    if not 16 <= e.bit_length() < 256:
        raise ValueError("e is out of range")

    while True:
        try:
            p, q = fips186_prime_gen(key_size, e=e, k=k)
        except Exception as ex:
            raise Exception(f"prime creation error: {ex}")
        key = PrivateKey(p, q, e)
        if key._d.bit_length() < key_size // 2:
            continue
        break

    m = secrets.randbelow(key._N - 2) + 1
    c = key.pub_key.encrypt(m)
    if key.decrypt(c) != m:
        raise Exception("pair-wise consistency failure")

    return (key.pub_key, key)


def fips186_prime_gen(
    n_len: int, e: int = 65537, k: int = 4
) -> tuple[int, int]:
    """Prime generation from Appendix A.1.3 of FIPS 186-5v2

    :param n_len: Desired length of modulus in bits
    :param e: Public exponent.
    :param k: Trials for primality testing.

    :raises ValueError: if :data:`e` is out of range or odd.
    :raises Exception:
        if it fails to find suitable primes after trying really hard.

    This insecurely deviates from the standard in allowing :data:`n_len`
    to be less than 2048.

    .. note::

        The condition that *p* and *q* differ in their
        most significant 100 bits is relaxed when
        :data:`n_len` < 2048.
    """

    # We don't enforce Step 1 for this toy

    # Step 2
    if not (16 <= e.bit_length() <= 256):
        raise ValueError("e is out of range")
    if e % 2 == 0:
        raise ValueError("e is odd in that it isn't odd")

    # We don't do step 3

    prime_size = n_len // 2

    # Standard says p and q must differ within their 100 most significant
    # bits, but that prevents us from generating some of our standard defying
    # small keys. So we will relax the condition.
    #
    # Standards say n_len must be at least 2024, and primes must differ
    # in first 100 bits. So we keep 100 for any key 2024.
    # We will reduce number for 2024 > n_len >= 512, and
    # eliminate it for n_len < 512.

    shift: int
    if n_len >= 512:
        # The standard
        shift = min(100, prime_size // 8 + 2)
    else:
        # Fermat can have his way with modulus.
        shift = 0

    i = 0  # Step 4.1
    while True:
        p = secrets.randbits(prime_size - 2)  # Step 4.2
        p += 0x3 << (prime_size - 2)

        # Step 4.3 options (without options)
        if p % 2 == 0:
            p += 1

        # Step 4.4 is not needed given how p is constructed
        # if p >> (prime_size - 2) != 0x03:  continue

        if gcd(p - 1, e) == 1:  # Step 4.5
            if probably_prime(p, k):
                break

        i += 1  # Step 4.6
        if i >= 5 * prime_size:  # Step 4.7
            raise Exception(f"Failure generating p: i = {i}")

    # q is much the same, but we also check that it isn't too close to p
    i = 0  # Step 5.1
    while True:
        q = secrets.randbits(prime_size - 2)  # Step 5.2
        q += 0x3 << (prime_size - 2)

        if q % 2 == 0:  # Step 5.3 without options
            q += 1

        # Step 5.4 is not needed given how q is constructed
        # if q >> (prime_size - 2) != 0x03:  continue

        if (p >> shift) == (q >> shift):  # Step 5.5
            continue

        if gcd(q - 1, e) == 1:  # Step 5.6
            if probably_prime(q, k):
                return p, q

        i += 1  # Step 5.7

        if i >= 5 * prime_size:  # Step 5.8
            raise Exception(f"Failure generating q: i = {i}")


def estimate_strength(key_size: int) -> int:
    """Strength estimate for key size.

    From NIST SP-800-56B r2 Appendix D.

    :param key_size: Modulus size in bits
    """

    pre_baked: dict[int, int] = {
        512: 56,
        1028: 80,
        2048: 112,
        3072: 128,
        4069: 152,
        6144: 176,
        8192: 200,
    }

    e = pre_baked.get(key_size)
    if e:
        return e

    # Else we calculate it

    # Formula from 800-56b Appendix D
    # ln2 = math.log(2)
    ln2 = 0.6931471805599453

    # I had a bug in simple math, so this got broken into lots
    # of intermediate values. I'm going to hope that the compiler
    # cleans this up.
    bln2 = key_size * ln2  # nBits x ln 2
    log_bln2 = math.log(bln2)
    croot_bln2 = bln2 ** (1 / 3)
    log_bln2_squared = log_bln2**2
    croot_log_squared = log_bln2_squared ** (1 / 3)

    estimate = (1.923 * croot_bln2 * croot_log_squared - 4.69) / ln2

    return utils.nearest_multiple(round(estimate), 8)
