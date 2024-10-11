from collections import namedtuple
from typing import Optional

from toy_crypto import rsa
from toy_crypto.nt import lcm, modinv


class TestCitm:
    """Tests using Cat in the Middle story"""

    # Not really a great set of tests, since the data I am testing against
    # was created with some of the same code I'm testing

    e = 17

    class Critter:
        def __init__(
            self,
            factors: tuple[int, int],
            expected_N: int,
            expected_d: Optional[int] = None,
        ) -> None:
            self.factors = factors
            self.expected_N = expected_N
            self.expected_d = expected_d

            self.test_data: list[tuple[int, int]] = []

    e = 17

    patty = Critter((107, 151), 16157, 1403)
    patty.test_data = [(1234, 8900)]

    molly = Critter((97, 43), 4171, 593)
    molly.test_data = [(1313, 530), (1729, 2826)]

    mr_talk = Critter((47, 89), 4183, 1905)
    mr_talk.test_data = [(1729, 2016)]

    def test_encrypt(self) -> None:
        for critter in [self.patty, self.molly, self.mr_talk]:
            p, q = critter.factors
            key = rsa.PrivateKey(p, q, pub_exponent=self.e)
            pubkey = key.pub_key

            for ptext, ctext in critter.test_data:
                assert ctext == pubkey.encrypt(ptext)

    def test_decrypt(self) -> None:
        for critter in [self.patty, self.molly, self.mr_talk]:
            p, q = critter.factors
            key = rsa.PrivateKey(p, q, pub_exponent=self.e)

            for ptext, ctext in critter.test_data:
                assert ptext == key.decrypt(ctext)

    def test_N(self) -> None:
        for critter in [self.patty, self.molly, self.mr_talk]:
            p, q = critter.factors
            key = rsa.PrivateKey(p, q, pub_exponent=self.e)
            pubkey = key.pub_key

            assert critter.expected_N == pubkey.N

    def test_d(self) -> None:
        for critter in [self.patty, self.molly, self.mr_talk]:
            p, q = critter.factors
            key = rsa.PrivateKey(p, q, pub_exponent=self.e)

            assert key._d == critter.expected_d


class TestSage:
    """Test data from SageMath Tutorial

    https://doc.sagemath.org/html/en/thematic_tutorials/numtheory_rsa.html

    The tutorial correctly points out that they way the primes
    were generated is inappropriate for real work.

    The tutorial uses phi directly instead of lcm(p-1, q-1).
    """

    # Don't use mersenne primes in real life
    p = (2**31) - 1
    q = (2**61) - 1
    e = 1850567623300615966303954877
    m = 72697676798779827668  # message

    n = 4951760154835678088235319297
    phi = 4951760152529835076874141700
    d = 4460824882019967172592779313
    c = 630913632577520058415521090

    λ = lcm(p - 1, q - 1)

    def test_encrypt(self) -> None:
        priv_key = rsa.PrivateKey(self.p, self.q, self.e)
        pub_key = priv_key.pub_key

        assert pub_key.encrypt(self.m) == self.c

    def test_decrypt(self) -> None:
        priv_key = rsa.PrivateKey(self.p, self.q, self.e)

        assert priv_key.decrypt(self.c) == self.m

    def test_N(self) -> None:
        priv_key = rsa.PrivateKey(self.p, self.q, self.e)
        pub_key = priv_key.pub_key

        assert self.n == pub_key.N

    def test_d(self) -> None:
        priv_key = rsa.PrivateKey(self.p, self.q, self.e)

        # We (almost certainly) get a smaller d where the lcm check matters
        if self.phi == self.λ:
            assert priv_key._d == self.d


class TestMG1977:
    # some utilities for doing the text to int and int to text from the
    # RSA-129 Challenge from Martin Gardner's 1977 article"
    abc = list(" ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    abc_index = {c: i for i, c in enumerate(abc)}

    @classmethod
    def encode(cls, text: str) -> int:
        result = 0
        for c in text:
            result *= 100
            result += cls.abc_index[c]
        return result

    @classmethod
    def decode(cls, number: int) -> str:
        chars: list[str] = []
        while True:
            number, rem = divmod(number, 100)
            chars.append(cls.abc[rem])
            if number == 0:
                break
        return "".join(reversed(chars))

    def test_magic(self) -> None:
        """Test the RSA-129 Challenge from Martin Gardner's 1977 article"""

        Challenge = namedtuple(
            "Challenge", ["modulus", "pub_exponent", "ctext"]
        )
        Solution = namedtuple("Solution", ["p", "q", "plaintext"])

        # From Martin Gardner's 1977
        challenge = Challenge(
            modulus=114381625757888867669235779976146612010218296721242362562561842935706935245733897830597123563958705058989075147599290026879543541,
            pub_exponent=9007,
            ctext=96869613754622061477140922254355882905759991124574319874695120930816298225145708356931476622883989628013391990551829945157815154,
        )

        # From Atkins et al 1995
        solution = Solution(
            p=3490529510847650949147849619903898133417764638493387843990820577,
            q=32769132993266709549961988190834461413177642967992942539798288533,
            plaintext="THE MAGIC WORDS ARE SQUEAMISH OSSIFRAGE",
        )

        pub_key = rsa.PublicKey(challenge.modulus, challenge.pub_exponent)

        # First test encryption
        plain_num: int = self.encode(solution.plaintext)
        ctext = pub_key.encrypt(plain_num)
        assert ctext == challenge.ctext

        # Now test decryption
        priv_key = rsa.PrivateKey(
            solution.p, solution.q, challenge.pub_exponent
        )
        assert priv_key == pub_key

        decrypted_num: int = priv_key.decrypt(ctext)
        decrypted: str = self.decode(decrypted_num)

        assert decrypted == solution.plaintext


class TestEq:
    # We will reuse magic values for this test, but anything should do
    p = 3490529510847650949147849619903898133417764638493387843990820577
    q = 32769132993266709549961988190834461413177642967992942539798288533
    e = 9007

    def test_pq_order(self) -> None:
        priv_pq = rsa.PrivateKey(self.p, self.q)
        priv_qp = rsa.PrivateKey(self.q, self.p)

        assert priv_pq == priv_qp

    def test_pub(self) -> None:
        priv_pq = rsa.PrivateKey(self.p, self.q, pub_exponent=self.e)
        priv_qp = rsa.PrivateKey(self.q, self.p, pub_exponent=self.e)

        assert priv_pq == priv_qp

    def test_pub_phi(self) -> None:
        """Key computed with 𝜑 is equivalent to key computed with λ."""

        key_lambda = rsa.PrivateKey(self.p, self.q, self.e)

        # can only construct key_phi by changing what would be private fields
        key_phi = rsa.PrivateKey(self.p, self.q, self.e)

        phi = (self.p - 1) * (self.q - 1)
        d_phi = modinv(key_phi.e, phi)

        key_phi._d = d_phi

        assert key_phi == key_lambda
