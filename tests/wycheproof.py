"""Loading and parsing Wycheproof test data.

Assumes you have a local copy, clone (submodule) of 
https://github.com/C2SP/wycheproof

Adapted from https://appsec.guide/docs/crypto/wycheproof/wycheproo_example/
"""

from collections.abc import Set, Collection
import os
from pathlib import Path
import json

# The example from Trail of Bits tests AEAD, but I'm not planning
# But I have commented out those fields here.
# The OAEP test data does need "value" converted from hex.
CONVERT_FROM_HEX: Set[str] = {
    "key",
    # "aad",
    # "iv",
    "msg",
    "ct",
    # "tag",
    "value",
}
"""JSON keys whose values should be converted from hex to bytes.

Please respect that the type ABC Set (unlike set) is supposed to be immutable.
"""

type WyVector = dict[str, object]


def dot_dir() -> Path:
    """The Path of the directory of the file from which this is called."""
    return Path(os.path.dirname(__file__))


DEFAULT_WP_ROOT = dot_dir() / "wycheproof"
"""Root of Wycheproof submodule."""


def load_vectors(
    path: Path | str,
    convert_keys: Set[str] = CONVERT_FROM_HEX,
    wy_root: Path = DEFAULT_WP_ROOT,
) -> Collection[WyVector]:
    """Load Wycheproof test vectors.

    :param path: Either absolute path or path relative to Wycheproof root.
    :param convert_keys: JSON keys to convert from hex to bytes
    :param wy_root: Path of copy/clone/submodule root of Wycheproof repository
    """

    if isinstance(path, str):
        path = Path(path)
    testVectors: list[WyVector] = []

    try:
        with open(path, "r") as f:
            wycheproof_json = json.loads(f.read())
    except FileNotFoundError:
        print(f"No Wycheproof file found at: {path}")
        return testVectors

    convert_attr = {"value"}
    for testGroup in wycheproof_json["testGroups"]:
        for tv in testGroup["tests"]:
            for attr in convert_attr:
                if attr in tv:
                    tv[attr] = bytes.fromhex(tv[attr])
            testVectors.append(tv)
    return testVectors
