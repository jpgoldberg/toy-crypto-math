"""Loading and parsing Wycheproof test data.

Assumes you have a local copy, clone (submodule) of
https://github.com/C2SP/wycheproof

Adapted from https://appsec.guide/docs/crypto/wycheproof/wycheproo_example/
"""

from collections.abc import Collection
import os
from pathlib import Path
import json
from jsonschema.protocols import Validator
from referencing import Resource, Registry


def collect_bigint_attrs(
    node: object,
    attr: str = "",
) -> set[str]:
    """Collects attributes in schema that are "format": "BigInt".

    :param node:
        object returned by something like ``json.load()``,
        or a node within such an object in the recursive calls.
    :param attr: is the name of the current object

    Wycheproof schemata use ``{"type": "string", "format": "BigInt"}``
    for attributes that are hexadecimal strings to be converted to int.
    We need to collect the names of such attributes.
    """

    acc: set[str] = set()

    if isinstance(node, dict):
        if node.get("format") == "BigInt" and node.get("type") == "string":
            acc.add(attr)
            return acc
        for key, value in node.items():
            acc |= collect_bigint_attrs(value, key)

    elif isinstance(node, list):
        for n in node:
            acc |= collect_bigint_attrs(n, "")
    return acc


type WyVector = dict[str, object]


def dot_dir() -> Path:
    """The Path of the directory of the file from which this is called."""
    return Path(os.path.dirname(__file__))


DEFAULT_WP_ROOT = dot_dir() / "wycheproof"
"""Root of Wycheproof submodule."""

DEFAUT_SCHEMATA = Path(DEFAULT_WP_ROOT / "schemas")


def retrieve_from_fs(directory: str = str(DEFAUT_SCHEMATA)) -> Resource:
    """Argument must be a str for reasons."""

    path = Path(directory)
    if not path.is_absolute():
        path = DEFAULT_WP_ROOT / path

    contents = json.loads(path.read_text())
    return Resource.from_contents(contents)


registry = Registry(retrieve=retrieve_from_fs)  # type: ignore[call-arg]


def load_vectors(
    path: Path | str,
    wy_root: Path = DEFAULT_WP_ROOT,
) -> Collection[WyVector]:
    """Load Wycheproof test vectors.

    :param path: Either absolute path or path relative to Wycheproof root.
    :param convert_keys: JSON keys to convert from hex to bytes
    :param wy_root: Path of copy/clone/submodule root of Wycheproof repository
    """

    if isinstance(path, str):
        path = Path(path)
    if not path.is_absolute():
        path = wy_root / path

    testVectors: list[WyVector] = []

    # We want to find the path to the schema from the path
    stem_name = path.stem
    schema_basename = stem_name + "_schema" + ".json"
    # Directory should be named "schemata",but oh well.
    schemata_dir = Path(wy_root / "schemas")
    schema_path = Path(schemata_dir / schema_basename)

    try:
        with open(schema_path, "r") as s:
            schema = json.load(s)
    except Exception as e:
        raise Exception(f"failed to load schema: {e}")

    try:
        with open(path, "r") as f:
            wycheproof_json = json.loads(f.read())
    except Exception as e:
        raise Exception(f"failed to load JSON: {e}")

    validator = Validator(
        schema=schema,
        registry=registry,
    )  # type: ignore[misc]
    try:
        validator.validate(wycheproof_json)
    except Exception as e:
        raise Exception(f"JSON validation failed: {e}")

    convert_attr = collect_bigint_attrs(schema)
    for testGroup in wycheproof_json["testGroups"]:
        for tv in testGroup["tests"]:
            for attr in convert_attr:
                if attr in tv:
                    tv[attr] = bytes.fromhex(tv[attr])
            testVectors.append(tv)
    return testVectors
