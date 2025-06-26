from collections import namedtuple
from typing import Optional


from toy_crypto import rsa
from toy_crypto.nt import lcm, modinv
from toy_crypto.utils import Rsa129


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

    # Don't use Mersenne primes in real life
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
    # encoder/decoder is in utils.Rsa129
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
        plain_num: int = Rsa129.encode(solution.plaintext)
        ctext = pub_key.encrypt(plain_num)
        assert ctext == challenge.ctext

        # Now test decryption
        priv_key = rsa.PrivateKey(
            solution.p, solution.q, challenge.pub_exponent
        )
        assert priv_key == pub_key

        decrypted_num: int = priv_key.decrypt(ctext)
        decrypted: str = Rsa129.decode(decrypted_num)

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


class TestMisc:
    p = 3490529510847650949147849619903898133417764638493387843990820577
    q = 32769132993266709549961988190834461413177642967992942539798288533

    def test_default_e(self) -> None:
        default_e = rsa.default_e()
        assert default_e == 65537

        priv_key = rsa.PrivateKey(self.p, self.q)

        assert priv_key.e == default_e


class TestOaep:
    # from 1024 bit key at
    # https://github.com/pyca/cryptography/blob/main/vectors/cryptography_vectors/asymmetric/RSA/pkcs-1v2-1d2-vec/oaep-vect.txt

    prime1 = bytes.fromhex("""
                d3 27 37 e7 26 7f fe 13 41 b2 d5 c0 d1 50 a8 1b
                58 6f b3 13 2b ed 2f 8d 52 62 86 4a 9c b9 f3 0a
                f3 8b e4 48 59 8d 41 3a 17 2e fb 80 2c 21 ac f1
                c1 1c 52 0c 2f 26 a4 71 dc ad 21 2e ac 7c a3 9d
            """)

    prime2 = bytes.fromhex("""
            cc 88 53 d1 d5 4d a6 30 fa c0 04 f4 71 f2 81 c7
            b8 98 2d 82 24 a4 90 ed be b3 3d 3e 3d 5c c9 3c
            47 65 70 3d 1d d7 91 64 2f 1f 11 6a 0d d8 52 be
            24 19 b2 af 72 bf e9 a0 30 e8 60 b0 28 8b 5d 77
        """)

    exponent = 65537

    # test vectors from https://github.com/bdauvergne/python-pkcs1/
    pkcs_vector: dict[str, bytes] = {
        "prime1": bytes.fromhex(
            "ee cf ae 81 b1 b9 b3 c9 08 81 0b 10 a1 b5 60 01"
            "99 eb 9f 44 ae f4 fd a4 93 b8 1a 9e 3d 84 f6 32"
            "12 4e f0 23 6e 5d 1e 3b 7e 28 fa e7 aa 04 0a 2d"
            "5b 25 21 76 45 9d 1f 39 75 41 ba 2a 58 fb 65 99"
        ),
        "prime2": bytes.fromhex(
            "c9 7f b1 f0 27 f4 53 f6 34 12 33 ea aa d1 d9 35"
            "3f 6c 42 d0 88 66 b1 d0 5a 0f 20 35 02 8b 9d 86"
            "98 40 b4 16 66 b4 2e 92 ea 0d a3 b4 32 04 b5 cf"
            "ce 33 52 52 4d 04 16 a5 a4 41 e7 00 af 46 15 03"
        ),
        "exponent_bytes": bytes([0x11]),
        "message": bytes.fromhex(
            "d4 36 e9 95 69 fd 32 a7c8 a0 5b bc 90 d3 2c 49"
        ),
        "seed": bytes.fromhex(
            "aa fd 12 f6 59 ca e6 34 89 b479 e5 07 6d de c2 f0 6c b5 8f"
        ),
        "seed_mask": bytes.fromhex(
            "41 87 0b 5a b0 29 e6 57 d9 57 50 b5 4c 28 3c 08 72 5d be a9"
        ),
        "ciphertext": bytes.fromhex(
            "12 53 e0 4d c0 a5 39 7b b4 4a 7a b8 7e 9b f2 a0 39 a3 3d 1e"
            "99 6f c8 2a 94 cc d3 00 74 c9 5d f7 63 72 20 17 06 9e 52 68"
            "da 5d 1c 0b 4f 87 2c f6 53 c1 1d f8 23 14 a6 79 68 df ea e2"
            "8d ef 04 bb 6d 84 b1 c3 1d 65 4a 19 70 e5 78 3b d6 eb 96 a0"
            "24 c2 ca 2f 4a 90 fe 9f 2e f5 c9 c1 40 e5 bb 48 da 95 36 ad"
            "87 00 c8 4f c9 13 0a de a7 4e 55 8d 51 a7 4d df 85 d8 b5 0d"
            "e9 68 38 d6 06 3e 09 55"
        ),
        "db": bytes.fromhex(
            "da 39 a3 ee 5e 6b 4b 0d 32 55 bf ef 95 60 18 90 af d8 07 09"
            "00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00"
            "00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00"
            "00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00"
            "00 00 00 00 00 00 00 00 00 00 01 d4 36 e9 95 69 fd 32 a7 c8"
            "a0 5b bc 90 d3 2c 49"
        ),
        "db_mask": bytes.fromhex(
            "06 e1 de b2 36 9a a5 a5 c7 07 d8 2c 8e 4e 93 24 8a c7 83 de"
            "e0 b2 c0 46 26 f5 af f9 3e dc fb 25 c9 c2 b3 ff 8a e1 0e 83"
            "9a 2d db 4c dc fe 4f f4 77 28 b4 a1 b7 c1 36 2b aa d2 9a b4"
            "8d 28 69 d5 02 41 21 43 58 11 59 1b e3 92 f9 82 fb 3e 87 d0"
            "95 ae b4 04 48 db 97 2f 3a c1 4e af f4 9c 8c 3b 7c fc 95 1a"
            "51 ec d1 dd e6 12 64"
        ),
        "masked_db": bytes.fromhex(
            "dc d8 7d 5c 68 f1 ee a8 f5 52 67 c3 1b 2e 8b b4 25 1f 84 d7"
            "e0 b2 c0 46 26 f5 af f9 3e dc fb 25 c9 c2 b3 ff 8a e1 0e 83"
            "9a 2d db 4c dc fe 4f f4 77 28 b4 a1 b7 c1 36 2b aa d2 9a b4"
            "8d 28 69 d5 02 41 21 43 58 11 59 1b e3 92 f9 82 fb 3e 87 d0"
            "95 ae b4 04 48 db 97 2f 3a c1 4f 7b c2 75 19 52 81 ce 32 d2"
            "f1 b7 6d 4d 35 3e 2d"
        ),
    }

    key1 = rsa.PrivateKey(
        int.from_bytes(prime1, byteorder="big"),
        int.from_bytes(prime2, byteorder="big"),
        pub_exponent=exponent,
    )

    def test_enc(self) -> None:
        class Vector:
            def __init__(
                self, name: str, message: str, seed: str, encryption: str
            ) -> None:
                self.name = name
                self.message = bytes.fromhex(message)
                self.seed = bytes.fromhex(seed)
                self.encryption = bytes.fromhex(encryption)

        vectors: list[Vector] = [
            Vector(
                name="Example 1.1",
                message="""
                    66 28 19 4e 12 07 3d b0 3b a9 4c da 9e f9 53 23
                    97 d5 0d ba 79 b9 87 00 4a fe fe 34
                """,
                seed="""
                    18 b7 76 ea 21 06 9d 69 77 6a 33 e9 6b ad 48 e1
                    dd a0 a5 ef 
                """,
                encryption="""
                    35 4f e6 7b 4a 12 6d 5d 35 fe 36 c7 77 79 1a 3f
                    7b a1 3d ef 48 4e 2d 39 08 af f7 22 fa d4 68 fb
                    21 69 6d e9 5d 0b e9 11 c2 d3 17 4f 8a fc c2 01
                    03 5f 7b 6d 8e 69 40 2d e5 45 16 18 c2 1a 53 5f
                    a9 d7 bf c5 b8 dd 9f c2 43 f8 cf 92 7d b3 13 22
                    d6 e8 81 ea a9 1a 99 61 70 e6 57 a0 5a 26 64 26
                    d9 8c 88 00 3f 84 77 c1 22 70 94 a0 d9 fa 1e 8c
                    40 24 30 9c e1 ec cc b5 21 00 35 d4 7a c7 2e 8a 
                """,
            )
        ]

        for v in vectors:
            ctext = self.key1.pub_key.oaep_encrypt(
                v.message, hash_id="sha1", mgf_id="mgf1SHA1", _seed=v.seed
            )
            assert ctext == v.encryption

    def test_enc_dec(self) -> None:
        p = int.from_bytes(self.prime1, "big")
        q = int.from_bytes(self.prime2, "big")
        key = rsa.PrivateKey(p, q, pub_exponent=self.exponent)

        plaintext = b"THE MAGIC WORDS ARE SQUEAMISH OSSIFRAGE"

        # As a sanity check, do primitive RSA with this key
        int_ptext = int.from_bytes(plaintext, "big")

        primitive_ctext = key.pub_key.encrypt(int_ptext)
        primitive_decrypted = key.decrypt(primitive_ctext)
        assert primitive_decrypted == int_ptext

        ctext = key.pub_key.oaep_encrypt(plaintext)
        decrypted = key.oaep_decrypt(ctext)

        assert plaintext == decrypted

    def test_mgf1(self) -> None:
        seed = self.pkcs_vector["seed"]
        db = self.pkcs_vector["db"]
        db_mask = rsa.Oaep.mgf1(seed, len(db), "sha1")
        assert db_mask == self.pkcs_vector["db_mask"]

    def test_enc_pkcs(self) -> None:
        """Test with vectors from Python PKCS"""

        p1 = int.from_bytes(self.pkcs_vector["prime1"], "big")
        p2 = int.from_bytes(self.pkcs_vector["prime2"], "big")
        e = int.from_bytes(self.pkcs_vector["exponent_bytes"], "big")

        key = rsa.PrivateKey(p1, p2, pub_exponent=e)
        pub_key = key.pub_key

        m = self.pkcs_vector["message"]
        ctext = pub_key.oaep_encrypt(
            m,
            hash_id="sha1",
            mgf_id="mgf1SHA1",
            _seed=self.pkcs_vector["seed"],
        )
        decrypted = key.oaep_decrypt(ctext, hash_id="sha1", mgf_id="mgf1SHA1")

        assert m == decrypted
        assert ctext == self.pkcs_vector["ciphertext"]
