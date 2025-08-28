"""A very few tests of wycheproof modules

Because other tests make use of the module, those tests would fail
if data could not be loaded correctly or contained bad data.
"""

from collections.abc import Sequence
import os
from pathlib import Path
import sys

import unittest
import pytest
from toy_crypto import wycheproof

from referencing.exceptions import Unresolvable

WP_ROOT = Path(os.path.dirname(__file__)) / "resources" / "wycheproof"
LOADER = wycheproof.Loader(WP_ROOT)


class TestLoading:
    def test_is_loader(self) -> None:
        assert isinstance(LOADER, wycheproof.Loader)

    def test_root_dir(self) -> None:
        assert WP_ROOT == LOADER._root_dir

    def test_registry(self) -> None:
        registry = LOADER.registry
        resolver = registry.resolver()

        try:
            _resolved = resolver.lookup("rsaes_oaep_decrypt_schema_v1.json")
        except Unresolvable as e:
            assert False, f"Resolution failed: {e}"


class TestAssumptions(unittest.TestCase):
    """Do all "testvectors_v1/*_test.json" files meet assumptions?"""

    # I need to learn how to use fixtures
    test_files: Sequence[Path] = list(
        WP_ROOT.glob("testvectors_v1/*_test.json")
    )

    @pytest.mark.skip(reason="Slow")
    def test_data(self) -> None:
        for file in self.test_files:
            file_name = file.name
            stem = file.stem
            try:
                data = LOADER.load(file_name)
            except Exception as e:
                assert False, f"loading error for {file_name}: {e}"

            # Are any of these empty?
            # (Ok, truthiness can be useful)
            assert data.algorithm, f"no algorithm in {stem}"
            # assert data.notes. # Notes can be empty
            assert data.groups, f"no groups in {stem}"
            assert data.test_count is not None, f"no count in {stem}"

            for g in data.groups:
                assert g.type is not None, f"missing group type in {stem}"

                for tc in g.tests:
                    assert tc.tcId > 0, f"weird tcID ({tc.tcId}) in {stem}"
                    assert tc.result in ("valid", "invalid", "acceptable"), (
                        f"weird result ({tc.result}) in {stem}"
                    )

    @pytest.mark.skip(reason="Slow")
    def test_formats(self) -> None:
        # Documented formats
        # https://github.com/C2SP/wycheproof/blob/main/doc/formats.md#data-types
        known = [
            "HexBytes", "BigInt", "Der", "Pem",
            "Asn", "EcCurve", "MdName",
            ]  # fmt: skip

        # Until https://github.com/C2SP/wycheproof/issues/165 is resolved
        known.append("Hex")
        for file in self.test_files:
            with self.subTest(file.stem):
                data = LOADER.load(file.name)
                if not data.schema_is_valid():
                    continue
                s_name: str = data.schema_file.name
                for p, f in data.formats.items():
                    # just to identify other problems
                    assert f in known, (
                        f"'{p}' has unknown format '{f}' in {s_name}"
                    )


class TestTests:
    def test_rsa_oaep_2046_sha1(self) -> None:
        data = LOADER.load("rsa_oaep_2048_sha1_mgf1sha1_test.json")

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
