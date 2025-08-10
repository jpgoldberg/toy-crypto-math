"""Loading and parsing Wycheproof test data.

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


def load_vectors(
    path: Path, convert_keys: Set[str] = CONVERT_FROM_HEX
) -> Collection[WyVector]:
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
