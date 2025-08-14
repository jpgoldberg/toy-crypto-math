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
        tests = WP_DATA.tests("rsa_oaep_2048_sha1_mgf1sha1_test.json")

        for test in tests:
            case = test.case
            if case["tcId"] == 1:
                assert test.valid
                assert isinstance(case["ct"], bytes)
                assert isinstance(case["msg"], bytes)
                assert isinstance(case["comment"], str)
                break
        else:
            assert False, "tcID 1 not found"


if __name__ == "__main__":
    sys.exit(pytest.main(args=[__file__]))
