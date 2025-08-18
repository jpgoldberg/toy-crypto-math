"""A very few tests of wycheproof modules

Because other tests make use of the module, those tests would fail
if data could not be loaded correctly or contained bad data.
"""

import os
from pathlib import Path
import sys

import pytest
from toy_crypto import wycheproof

WP_ROOT = Path(os.path.dirname(__file__)) / "resources" / "wycheproof"
WP_DATA = wycheproof.Loader(WP_ROOT)


class TestLoading:
    def test_is_loader(self) -> None:
        assert isinstance(WP_DATA, wycheproof.Loader)

    def test_root_dir(self) -> None:
        assert WP_ROOT == WP_DATA._root_dir


class TestTests:
    def test_rsa_oaep_2046_sha1(self) -> None:
        data = WP_DATA.load_json("rsa_oaep_2048_sha1_mgf1sha1_test.json")

        assert data.header == str(
            "Test vectors of type RsaOeapDecrypt are"
            " intended to check the decryption of RSA"
            " encrypted ciphertexts."
        )

        for group in data.groups:
            assert isinstance(group["d"], int)
            assert isinstance(group["keysize"], int)
            assert isinstance(group["mgf"], str)

            for tc in group.tests:
                assert tc.tcId > 0

                match tc.tcId:
                    case 1:
                        assert tc.comment == ""
                        assert tc.valid
                        assert not tc.flags

                    case 3:
                        assert tc.comment == ""
                        assert tc.valid
                        assert not tc.flags
                        assert tc["msg"] == bytes.fromhex("54657374")

                    case 12:
                        assert tc.comment == "first byte of l_hash modified"
                        assert tc.invalid
                        assert len(tc.flags) == 1
                        assert tc.has_flag("InvalidOaepPadding")

                    case 21:
                        assert tc.comment == "seed is all 1"
                        assert tc.valid

                    case 32:
                        assert tc.comment == "em has a large hamming weight"
                        assert tc.valid
                        label = tc["label"]
                        assert isinstance(label, bytes)
                        assert len(label) == 24
                        assert not tc.has_flag("InvalidOaepPadding")
                        assert tc.has_flag("Constructed")

                    case _:
                        assert tc.result in ("valid", "invalid", "acceptable")
                        assert isinstance(tc["ct"], bytes)
                        assert isinstance(tc["msg"], bytes)


if __name__ == "__main__":
    sys.exit(pytest.main(args=[__file__]))
