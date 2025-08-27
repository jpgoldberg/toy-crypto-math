"""A very few tests of wycheproof modules

Because other tests make use of the module, those tests would fail
if data could not be loaded correctly or contained bad data.
"""

import os
from pathlib import Path
import sys

import pytest
from toy_crypto import wycheproof

from referencing.exceptions import Unresolvable

WP_ROOT = Path(os.path.dirname(__file__)) / "resources" / "wycheproof"
WP_DATA = wycheproof.Loader(WP_ROOT)


class TestLoading:
    def test_is_loader(self) -> None:
        assert isinstance(WP_DATA, wycheproof.Loader)

    def test_root_dir(self) -> None:
        assert WP_ROOT == WP_DATA._root_dir

    def test_registry(self) -> None:
        registry = WP_DATA.registry
        resolver = registry.resolver()

        try:
            _resolved = resolver.lookup("rsaes_oaep_decrypt_schema_v1.json")
        except Unresolvable as e:
            assert False, f"Resolution failed: {e}"


class TestTests:
    def test_rsa_oaep_2046_sha1(self) -> None:
        data = WP_DATA.load("rsa_oaep_2048_sha1_mgf1sha1_test.json")

        formats = data.formats
        assert "privateExponent" in formats

        assert data.header == str(
            "Test vectors of type RsaOeapDecrypt check decryption with OAEP."
        )

        for group in data.groups:
            privateKey = group.other_data["privateKey"]
            assert isinstance(privateKey, dict)

            wycheproof.deserialize_top_level(privateKey, data.formats)
            d = privateKey["privateExponent"]
            assert isinstance(d, int)
            assert isinstance(group.other_data["keySize"], int)
            assert isinstance(group.other_data["mgf"], str)

            for tc in group.tests:
                assert tc.tcId > 0

                match tc.tcId:
                    case 1:
                        assert tc.comment == ""
                        assert tc.valid
                        assert tc.has_flag("Normal")

                    case 3:
                        assert tc.comment == ""
                        assert tc.valid
                        assert "Normal" in tc.flags
                        assert tc.other_data["msg"] == bytes.fromhex(
                            "54657374"
                        )

                    case 12:
                        assert tc.comment == "first byte of l_hash modified"
                        assert tc.invalid
                        assert len(tc.flags) == 1
                        assert tc.has_flag("InvalidOaepPadding")

                    case 22:
                        assert tc.comment == "seed is all 1"
                        assert tc.valid

                    case 29:
                        assert tc.comment == "ciphertext is empty"
                        assert tc.has_flag("InvalidCiphertext")
                        assert tc.invalid

                    case 34:
                        assert tc.comment == "em has a large hamming weight"
                        assert tc.valid
                        label = tc.other_data["label"]
                        assert isinstance(label, bytes)
                        assert len(label) == 24
                        assert not tc.has_flag("InvalidOaepPadding")
                        assert tc.has_flag("Constructed")
                        assert tc.has_flag("EncryptionWithLabel")

                    case _:
                        assert tc.result in ("valid", "invalid", "acceptable")
                        assert isinstance(tc.other_data["ct"], bytes)
                        assert isinstance(tc.other_data["msg"], bytes)


if __name__ == "__main__":
    sys.exit(pytest.main(args=[__file__]))
